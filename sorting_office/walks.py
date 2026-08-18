"""Putting a message on a walk, by the address it was delivered to.

The mail domain is a catch-all, so each site gets its own alias and the alias is
the classification signal. A walk is a named set of addresses handled together,
with one retention behaviour for the lot.

The rules themselves live in a store on the mini PC rather than in this repo —
they name every site signed up to, and this repo is public. See
[ADR 0007](../docs/decisions/0007-rules-in-a-database.md). Everything here takes
rules as an argument, so none of it needs that store to exist.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from fnmatch import fnmatchcase

from sorting_office.behaviours import Behaviour, KeepIndefinitely


@dataclass(frozen=True)
class WalkRule:
    """A rule putting one address, or a pattern of addresses, on a walk.

    ``address`` is either an exact alias (``stamp-exchange@sorting-office.test``)
    or a pattern containing ``*`` (``*-weekly@sorting-office.test``). Matching
    ignores case, because an address that differs only in case is the same
    address.
    """

    walk: str
    address: str

    @property
    def is_pattern(self) -> bool:
        return "*" in self.address or "?" in self.address

    def matches(self, address: str) -> bool:
        candidate = address.casefold()
        pattern = self.address.casefold()
        return fnmatchcase(candidate, pattern) if self.is_pattern else candidate == pattern

    @property
    def precedence(self) -> tuple[int, int, str, str]:
        """How this rule ranks against another that matches the same address.

        An exact rule beats a pattern. Between two patterns, the one with more
        literal characters is the more specific — ``parcels-*@`` says more about
        an address than ``*@`` does. The walk and address break any
        remaining tie so the answer is stable rather than dependent on the order
        the rules were loaded in: two rules genuinely competing for one address
        is a conflict the Counter refuses at the point of saving, and a duty in
        progress should not be the thing that discovers it.
        """
        literal_length = sum(1 for character in self.address if character not in "*?")
        return (0 if self.is_pattern else 1, literal_length, self.walk, self.address)


@dataclass(frozen=True)
class Walk:
    """A named set of addresses handled together, and how long its mail is kept.

    A walk that does not state a behaviour keeps its mail indefinitely. The
    conservative default is deliberate: the wrong answer should be "kept too
    long", never "deleted too early".
    """

    name: str
    behaviour: Behaviour = field(default_factory=KeepIndefinitely)


def assign_walk(address: str, rules: Iterable[WalkRule]) -> str | None:
    """Return the walk for ``address``, or ``None`` if no rule matches.

    A message goes on exactly one walk. ``None`` is the Dead Letter Office case:
    the address has never been seen before, which happens the moment an alias is
    typed into a signup form. That is normal rather than exceptional, so it is a
    return value and not an error — a duty carries on, and the address is raised
    for triage.
    """
    matching = [rule for rule in rules if rule.matches(address)]
    if not matching:
        return None
    return max(matching, key=lambda rule: rule.precedence).walk
