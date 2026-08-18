"""What the rest of the package needs to know about a message.

Deliberately not a mail library. This is the handful of facts a classification or
retention decision is allowed to depend on, so that both can be reasoned about
without a mailbox.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True)
class Message:
    """A collected message, as far as the decision logic is concerned.

    Attributes:
        id: The message's own identity, carried over from collection. Collection
            keys on it so a repeated duty cannot store a second copy, and every
            decision here refers to a message by it.
        delivered_to: The alias the message was addressed to. The domain is a
            catch-all, so this is the classification signal — it identifies the
            site that sent the mail.
        postmark: When *we* accepted the message, recorded at collection. Not the
            sender's ``Date:`` header, which the sender controls.
        read: Whether the message has been read, read back from the local
            mailbox's ``\\Seen`` flag rather than tracked separately.
        walk: The walk the message is on, or ``None`` if its address has no rule
            yet and it is waiting in the Dead Letter Office.
    """

    id: str
    delivered_to: str
    postmark: datetime
    read: bool = False
    walk: str | None = None

    def on_walk(self, walk: str | None) -> Message:
        """Return this message assigned to ``walk``.

        Used both when classification first assigns a walk and when a miss-sort
        is corrected, which is the same operation seen twice.
        """
        return replace(self, walk=walk)
