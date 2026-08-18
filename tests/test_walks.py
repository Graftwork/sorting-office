"""Putting a message on a walk by the address it was delivered to.

Every address here is invented, and deliberately reads as mail a sorting office
would actually get. Real walk rules name every site the owner has signed up to,
which is why they live in a store on the mini PC and not in this repo — see
docs/decisions/0007-rules-in-a-database.md.
"""

from __future__ import annotations

import pytest

from sorting_office.walks import WalkRule, assign_walk

PARCELS_WEEKLY = WalkRule(walk="headlines", address="parcels-weekly@sorting-office.test")
ANY_WEEKLY = WalkRule(walk="general-marketing", address="*-weekly@sorting-office.test")
ANYTHING = WalkRule(walk="general-marketing", address="*@sorting-office.test")

RULES = [PARCELS_WEEKLY, ANY_WEEKLY, ANYTHING]


@pytest.mark.spec("walks/a-known-address-puts-a-message-on-its-walk")
def test_a_known_address_is_put_on_its_walk():
    assert assign_walk("parcels-weekly@sorting-office.test", RULES) == "headlines"


@pytest.mark.spec("walks/a-message-is-assigned-exactly-one-walk")
def test_one_address_yields_exactly_one_walk():
    # All three rules match this address, and the answer is still a single walk
    # rather than a list to be reconciled later.
    assigned = assign_walk("franking-weekly@sorting-office.test", RULES)

    assert isinstance(assigned, str)
    assert assigned in {rule.walk for rule in RULES}


@pytest.mark.spec("walks/an-unknown-address-does-not-stop-the-run")
def test_an_unknown_address_does_not_raise():
    # A new alias appears the moment it is typed into a signup form, so this is
    # an everyday event. It has to be a return value, not an exception.
    assert assign_walk("stamp-exchange@sorting-office.test", [PARCELS_WEEKLY, ANY_WEEKLY]) is None


@pytest.mark.spec("walks/an-unknown-address-is-raised-for-triage")
def test_an_unknown_address_is_raised_rather_than_guessed():
    # No walk is how classification raises an address for triage. Recording it in
    # the Dead Letter Office is that capability's own promise, and its own task.
    assert assign_walk("stamp-exchange@sorting-office.test", [PARCELS_WEEKLY]) is None


@pytest.mark.spec("walks/the-most-specific-matching-rule-wins")
def test_the_most_specific_rule_wins():
    # An exact rule beats a pattern...
    assert assign_walk("parcels-weekly@sorting-office.test", RULES) == "headlines"

    # ...and between two patterns, the one saying more about the address wins.
    detailed = WalkRule(walk="detailed", address="*-weekly@sorting-office.test")
    vague = WalkRule(walk="vague", address="*@sorting-office.test")
    assert assign_walk("franking-weekly@sorting-office.test", [vague, detailed]) == "detailed"


@pytest.mark.spec("walks/matching-an-address-is-case-insensitive")
def test_case_does_not_change_the_answer():
    assert assign_walk("Parcels-Weekly@Sorting-Office.test", RULES) == "headlines"
    assert assign_walk("Franking-WEEKLY@sorting-office.test", [ANY_WEEKLY]) == "general-marketing"


def test_rule_order_does_not_change_the_answer():
    # Two rules competing for one address is a conflict the Counter refuses when
    # it is saved. If one ever reaches a duty, the duty is not the place to find
    # out about it, so the answer must not depend on load order.
    forwards = assign_walk("franking-weekly@sorting-office.test", RULES)
    backwards = assign_walk("franking-weekly@sorting-office.test", list(reversed(RULES)))

    assert forwards == backwards
