"""Reconciling what is in the mailbox against what the walks say to keep.

Retention is not a verdict stamped on a message when it arrives. Read state
changes afterwards and newer messages arrive later, so this re-evaluates
everything currently held against its current state, every time it runs.

**This module decides; it does not act.** :func:`reconcile` returns a plan and
changes nothing — not the messages it was given, not a mailbox, not anything.
Carrying a plan out is a separate, explicit step somewhere else. Dry run is
therefore not a setting anyone has to remember here: deciding is the only thing
this code can do.

The plan's whole vocabulary is :class:`Action`, and there is no delete in it.
Pruning means moving a message to Trash; see
[ADR 0008](../docs/decisions/0008-pruning-moves-to-trash.md).
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sorting_office.mail import Message
from sorting_office.walks import Walk

#: What a message on no walk is reported as, in place of a behaviour's label.
DEAD_LETTER_LABEL = "none — awaiting triage"


class Action(Enum):
    """What retention can decide to do with a message.

    These two are the entire vocabulary, on purpose. Deleting is not an action
    retention is able to name, so no bug in a behaviour, no wrong walk rule and
    no mistake in this module can lose mail — the worst it can do is put
    something in Trash that should have stayed put.
    """

    KEEP = "keep"
    TO_TRASH = "to-trash"


@dataclass(frozen=True)
class Verdict:
    """What a reconciliation decided about one message, and why.

    The walk and behaviour travel with the decision rather than being looked up
    again later, because the Counter has to be able to show why a message was
    pruned in order for anyone to trust the thing enough to let it run.
    """

    message_id: str
    action: Action
    walk: str | None
    behaviour: str
    reason: str

    @property
    def kept(self) -> bool:
        return self.action is Action.KEEP


@dataclass(frozen=True)
class Plan:
    """What a reconciliation would do, if somebody carried it out."""

    verdicts: tuple[Verdict, ...]

    @property
    def to_trash(self) -> tuple[Verdict, ...]:
        return tuple(verdict for verdict in self.verdicts if verdict.action is Action.TO_TRASH)

    @property
    def kept(self) -> tuple[Verdict, ...]:
        return tuple(verdict for verdict in self.verdicts if verdict.kept)

    @property
    def ids_to_trash(self) -> frozenset[str]:
        return frozenset(verdict.message_id for verdict in self.to_trash)


def reconcile(
    messages: Iterable[Message],
    walks: Mapping[str, Walk],
    *,
    now: datetime,
) -> Plan:
    """Decide what to keep and what to move to Trash, and return it as a plan.

    Messages on no walk, and messages on a walk with no rule loaded for it, are
    kept and reported as awaiting triage. An address nobody has classified yet is
    an everyday event, not a failure, and guessing a behaviour for it could
    delete something that mattered.

    Running this twice over unchanged state gives the same plan twice; carrying
    the plan out is what makes the second run find nothing left to do.
    """
    held = list(messages)

    on_each_walk: dict[str | None, list[Message]] = defaultdict(list)
    for message in held:
        on_each_walk[message.walk].append(message)

    pruning: dict[str, str] = {}
    for walk_name, on_this_walk in on_each_walk.items():
        walk = walks.get(walk_name) if walk_name is not None else None
        if walk is None:
            continue
        pruning.update(walk.behaviour.to_prune(on_this_walk, now))

    verdicts: list[Verdict] = []
    for message in held:
        walk = walks.get(message.walk) if message.walk is not None else None
        behaviour = walk.behaviour.label if walk is not None else DEAD_LETTER_LABEL

        if (reason := pruning.get(message.id)) is not None:
            action, explanation = Action.TO_TRASH, reason
        elif walk is None:
            action, explanation = Action.KEEP, "no walk rule for this address yet"
        else:
            action, explanation = Action.KEEP, "kept by this walk's behaviour"

        verdicts.append(
            Verdict(
                message_id=message.id,
                action=action,
                walk=message.walk,
                behaviour=behaviour,
                reason=explanation,
            )
        )

    return Plan(verdicts=tuple(verdicts))
