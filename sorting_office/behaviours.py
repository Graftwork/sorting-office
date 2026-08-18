"""The four retention behaviours, as decisions over message metadata.

Each behaviour answers one question: given every message currently on a walk,
which of them should be pruned? None of them can do anything about the answer —
they return ids and reasons, and :mod:`sorting_office.retention` turns that into
a plan somebody else carries out.

Pruning means moving a message to Trash. It never means deleting; see
[ADR 0008](../docs/decisions/0008-pruning-moves-to-trash.md).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol, runtime_checkable

from sorting_office.mail import Message

#: How long a timer walk holds a message when it does not set its own age.
DEFAULT_TIMER_AGE = timedelta(days=7)


@runtime_checkable
class Behaviour(Protocol):
    """What every retention behaviour can do."""

    #: How this behaviour is named in a report at the Counter.
    label: str

    def to_prune(self, messages: Sequence[Message], now: datetime) -> dict[str, str]:
        """Return ``{message id: reason}`` for the messages that should be pruned.

        Messages absent from the mapping are kept. Implementations must not
        depend on the order they are given, and must return the same answer for
        the same input, which is what makes a reconciliation safe to repeat.
        """
        ...


def _newest_first(messages: Sequence[Message]) -> list[Message]:
    """Order messages by arrival, newest first.

    The id breaks ties so that two messages sharing a postmark still come out in
    a stable order — otherwise a reconciliation could prune a different one of
    them each time it ran.
    """
    return sorted(messages, key=lambda message: (message.postmark, message.id), reverse=True)


@dataclass(frozen=True)
class KeepRecent:
    """Keep the newest ``keep`` messages on the walk and prune the rest.

    For daily headlines and general marketing, where only the most recent mail is
    worth having. The default of one is the all-or-nothing case; a higher count
    holds a run of them — a week of a daily paper, say — and then drops the
    oldest as new ones arrive.

    Superseding goes by arrival order alone, whether or not a message has been
    read. Not reading a walk is not a reason for it to grow without limit, and
    since pruning is a move to Trash, an unread message that gets superseded is
    still recoverable.
    """

    keep: int = 1
    label: str = "keep-recent"

    def __post_init__(self) -> None:
        if self.keep < 1:
            raise ValueError(f"a keep-recent walk must keep at least one message, not {self.keep}")

    def to_prune(self, messages: Sequence[Message], now: datetime) -> dict[str, str]:
        superseded = _newest_first(messages)[self.keep :]
        return {
            message.id: f"superseded by a newer arrival; this walk keeps {self.keep}"
            for message in superseded
        }


@dataclass(frozen=True)
class PosteRestante:
    """Keep a message while it is unread; prune it once it has been read.

    Mail held at the office until called for. For comics, reviews and commentary
    — worth keeping however long it takes to get to, and worth nothing once read.
    """

    label: str = "poste restante"

    def to_prune(self, messages: Sequence[Message], now: datetime) -> dict[str, str]:
        return {message.id: "read" for message in messages if message.read}


@dataclass(frozen=True)
class Timer:
    """Prune a message once it is older than ``age``, read or not.

    For delivery notifications and anything else with a fixed short shelf life,
    where nobody going back to read it does not make it worth keeping.
    """

    age: timedelta = DEFAULT_TIMER_AGE
    label: str = "timer"

    def to_prune(self, messages: Sequence[Message], now: datetime) -> dict[str, str]:
        return {
            message.id: f"older than {self.age.days} days"
            for message in messages
            if now - message.postmark > self.age
        }


@dataclass(frozen=True)
class KeepIndefinitely:
    """Never prune. For purchase confirmations and anything else that must survive."""

    label: str = "keep indefinitely"

    def to_prune(self, messages: Sequence[Message], now: datetime) -> dict[str, str]:
        return {}
