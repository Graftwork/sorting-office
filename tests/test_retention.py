"""The four retention behaviours, and the reconciliation that applies them.

Every address here is invented; see the note in ``test_walks.py``.

Reconciliation decides and never acts, so "pruned" in these tests means the plan
says to move a message to Trash. Confirming that a message moved to Trash is
still readable from a normal client belongs to the mailbox work, not here.
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime, timedelta

import pytest

from sorting_office.behaviours import (
    DEFAULT_TIMER_AGE,
    KeepIndefinitely,
    KeepRecent,
    PosteRestante,
    Timer,
)
from sorting_office.mail import Message
from sorting_office.retention import Action, reconcile
from sorting_office.walks import Walk

NOW = datetime(2026, 8, 14, 9, 0, tzinfo=UTC)

WALKS = {
    "headlines": Walk("headlines", KeepRecent()),
    "the-week": Walk("the-week", KeepRecent(keep=7)),
    "comics": Walk("comics", PosteRestante()),
    "deliveries": Walk("deliveries", Timer(timedelta(days=3))),
    "reminders": Walk("reminders", Timer()),
    "receipts": Walk("receipts", KeepIndefinitely()),
}


def message(
    identifier: str,
    *,
    walk: str | None = None,
    days_old: int = 0,
    read: bool = False,
) -> Message:
    return Message(
        id=identifier,
        delivered_to="parcels-weekly@sorting-office.test",
        postmark=NOW - timedelta(days=days_old),
        read=read,
        walk=walk,
    )


def pruned_ids(messages, walks=WALKS, now=NOW) -> frozenset[str]:
    return reconcile(messages, walks, now=now).ids_to_trash


def carry_out(plan, messages) -> list[Message]:
    """Do what a plan says, the way the mailbox step eventually will."""
    return [held for held in messages if held.id not in plan.ids_to_trash]


# --- Keep-recent ------------------------------------------------------------


@pytest.mark.spec("retention/a-new-arrival-supersedes-the-previous-one")
def test_a_newer_arrival_supersedes_the_older():
    yesterday = message("yesterday", walk="headlines", days_old=1)
    today = message("today", walk="headlines")

    assert pruned_ids([yesterday, today]) == {"yesterday"}


@pytest.mark.spec("retention/the-only-message-on-the-walk-is-kept")
def test_a_lone_message_is_kept():
    assert pruned_ids([message("only", walk="headlines", days_old=400)]) == frozenset()


@pytest.mark.spec("retention/an-unread-message-is-superseded-like-any-other")
def test_being_unread_does_not_save_a_superseded_message():
    # Otherwise a walk nobody reads grows without limit, which is the problem
    # this project started from. Safe because pruning is a move to Trash.
    older = message("older", walk="headlines", days_old=1, read=False)
    newer = message("newer", walk="headlines", read=False)

    assert pruned_ids([older, newer]) == {"older"}


@pytest.mark.spec("retention/a-walk-can-keep-more-than-one")
def test_a_walk_can_hold_a_run_of_messages():
    # A week of a daily paper: the eighth arrival pushes the oldest out.
    week = [message(f"day-{day}", walk="the-week", days_old=day) for day in range(8)]

    assert pruned_ids(week) == {"day-7"}


def test_a_keep_recent_walk_must_keep_at_least_one():
    # Keeping zero would make this behaviour a delete-everything rule, which is
    # not something a walk should be able to say by accident.
    with pytest.raises(ValueError, match="at least one"):
        KeepRecent(keep=0)


# --- Poste restante ---------------------------------------------------------


@pytest.mark.spec("retention/an-unread-message-is-kept")
def test_an_unread_message_is_kept_however_old():
    assert pruned_ids([message("unread", walk="comics", days_old=400)]) == frozenset()


@pytest.mark.spec("retention/a-read-message-becomes-eligible-for-pruning")
def test_a_read_message_becomes_eligible():
    assert pruned_ids([message("read", walk="comics", read=True)]) == {"read"}


# --- Timer ------------------------------------------------------------------


@pytest.mark.spec("retention/a-message-older-than-the-timer-is-pruned")
def test_a_message_past_its_timer_is_pruned():
    assert pruned_ids([message("stale", walk="deliveries", days_old=5, read=True)]) == {"stale"}


@pytest.mark.spec("retention/an-unread-message-is-still-pruned-by-the-timer")
def test_the_timer_ignores_read_state():
    assert pruned_ids([message("stale", walk="deliveries", days_old=5)]) == {"stale"}


@pytest.mark.spec("retention/a-message-within-the-timer-is-kept")
def test_a_message_inside_its_timer_is_kept():
    assert pruned_ids([message("fresh", walk="deliveries", days_old=1)]) == frozenset()


@pytest.mark.spec("retention/a-timer-walk-with-no-age-set-uses-seven-days")
def test_an_unconfigured_timer_walk_uses_the_default_age():
    assert timedelta(days=7) == DEFAULT_TIMER_AGE

    just_inside = message("day-six", walk="reminders", days_old=6)
    just_outside = message("day-eight", walk="reminders", days_old=8)

    assert pruned_ids([just_inside, just_outside]) == {"day-eight"}


# --- Keep indefinitely ------------------------------------------------------


@pytest.mark.spec("retention/an-old-read-message-is-still-kept")
def test_keep_indefinitely_survives_age_and_reading():
    receipt = message("receipt", walk="receipts", days_old=400, read=True)

    assert pruned_ids([receipt]) == frozenset()


@pytest.mark.spec("walks/an-unknown-address-is-never-pruned-by-default")
def test_a_message_on_no_walk_is_never_pruned():
    # Old, read, and on no walk: every behaviour that could apply would prune it,
    # and none of them does, because guessing could delete something that
    # mattered.
    waiting = message("untriaged", walk=None, days_old=400, read=True)

    plan = reconcile([waiting], WALKS, now=NOW)

    assert plan.ids_to_trash == frozenset()
    assert plan.verdicts[0].kept
    assert "triage" in plan.verdicts[0].behaviour


@pytest.mark.spec("walks/a-miss-sorted-message-is-moved-to-the-right-walk")
def test_reassigning_a_walk_changes_which_behaviour_governs():
    miss_sorted = message("confirmation", walk="deliveries", days_old=5)
    assert pruned_ids([miss_sorted]) == {"confirmation"}

    corrected = miss_sorted.on_walk("receipts")
    assert pruned_ids([corrected]) == frozenset()


# --- Reconciling ------------------------------------------------------------


@pytest.mark.spec("retention/reading-a-message-later-makes-it-eligible")
def test_reading_a_message_after_collection_makes_it_eligible():
    comic = message("comic", walk="comics", days_old=2)
    assert pruned_ids([comic]) == frozenset()

    # Read state is read back from the mailbox at each reconciliation rather than
    # decided once at collection, so this is all it takes.
    assert pruned_ids([dataclasses.replace(comic, read=True)]) == {"comic"}


@pytest.mark.spec("retention/reconciliation-is-safe-to-repeat")
def test_a_second_run_over_unchanged_state_prunes_nothing_further():
    held = [
        message("yesterday", walk="headlines", days_old=1),
        message("today", walk="headlines"),
        message("read-comic", walk="comics", read=True),
    ]

    first = reconcile(held, WALKS, now=NOW)
    remaining = carry_out(first, held)
    second = reconcile(remaining, WALKS, now=NOW)

    assert first.ids_to_trash == {"yesterday", "read-comic"}
    assert second.ids_to_trash == frozenset()


@pytest.mark.spec("retention/reconciliation-reports-without-changing-anything")
def test_reconciliation_changes_nothing_it_was_given():
    held = [
        message("yesterday", walk="headlines", days_old=1),
        message("today", walk="headlines"),
    ]
    before = tuple(held)

    plan = reconcile(held, WALKS, now=NOW)

    assert [verdict.message_id for verdict in plan.to_trash] == ["yesterday"]
    assert [verdict.message_id for verdict in plan.kept] == ["today"]
    assert tuple(held) == before


@pytest.mark.spec("retention/a-pruned-message-is-moved-to-trash-rather-than-deleted")
def test_pruning_is_a_move_to_trash():
    held = [
        message("yesterday", walk="headlines", days_old=1),
        message("today", walk="headlines"),
    ]

    plan = reconcile(held, WALKS, now=NOW)

    assert [verdict.action for verdict in plan.to_trash] == [Action.TO_TRASH]


@pytest.mark.spec("retention/retention-cannot-express-a-delete")
def test_there_is_no_delete_to_reach_for():
    # Not a naming preference: deleting is not an outcome this layer can name, so
    # no bug in a behaviour or a rule can lose mail.
    assert {action.value for action in Action} == {"keep", "to-trash"}


@pytest.mark.spec("retention/every-decision-carries-its-reason")
def test_every_verdict_names_its_walk_behaviour_and_reason():
    held = [
        message("yesterday", walk="headlines", days_old=1),
        message("today", walk="headlines"),
        message("untriaged", walk=None),
    ]

    plan = reconcile(held, WALKS, now=NOW)

    assert len(plan.verdicts) == len(held)
    for verdict in plan.verdicts:
        assert verdict.behaviour
        assert verdict.reason

    superseded = next(verdict for verdict in plan.to_trash)
    assert superseded.walk == "headlines"
    assert superseded.behaviour == "keep-recent"
    assert "superseded" in superseded.reason
