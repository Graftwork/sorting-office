# ADR 0012: The postbox's local bridge runs in a container

- **Status:** proposed
- **Date:** 2026-08-24

## Context

[ADR 0001](0001-where-it-runs.md) already anticipated this, in passing: "Anything
the postbox needs in order to expose IMAP — some providers only do so through a
local bridge process — runs there headless, as a systemd service." That assumed
systemd without examining the alternative. Now that the postbox in question is
one of the providers this applies to, the packaging choice is real rather than
hypothetical, and worth its own decision rather than inheriting ADR 0001's
passing assumption by default.

Two costs are inherent to running this kind of bridge at all, independent of how
it's packaged:

- **A one-time interactive pairing step.** Login, and a second factor where the
  account has one, has to happen through the bridge's own interactive flow at
  least once. Nothing committed to this repo can complete that unassisted — the
  same shape as `mise trust` or the cloud environment Setup Script paste
  ([ADR 0010](0010-mise-unpinned-via-mise-run.md)): automatable right up to a
  step only a human can do.
- **No headless credential store by default.** These bridges are built
  GUI-first and normally rely on a desktop keychain to hold the credentials they
  generate. A headless box doesn't have one, so a filesystem-backed substitute
  has to be configured instead — documented behaviour for the bridge in
  question, not a workaround being invented here.

A third fact specific to the packaging question: no official container image is
published for this bridge. Whatever runs it has to be built or vetted directly,
which matters more here than it did for [ADR 0003](0003-real-local-mailbox.md)'s
Dovecot or [ADR 0005](0005-n8n-execution-engine.md)'s n8n — this is the one
component that holds live mail credentials.

## Decision

Run the bridge in a container on the mini PC, built from a minimal image that
installs the bridge from the provider's own official release and adds the
filesystem-backed credential store it needs to run headless. Not a prebuilt
third-party image — the same reasoning already applied to Dovecot in ADR 0003:
a thin custom image beats trusting someone else's bundle, more so here because
this one carries credentials rather than just a well-known protocol server.

- The one-time interactive pairing runs by execing directly into the running
  container. The credential store is a mounted volume, so a container restart
  doesn't repeat it.
- The container's IMAP/SMTP listener is bound only to the loopback or tailnet
  address the sweeper actually reaches it on — never `0.0.0.0` — so this stays
  inside ADR 0001's Tailscale-only boundary rather than quietly widening it.

Marked **proposed**, not accepted, the same way ADR 0005 marks n8n: nothing is
built yet. This should be confirmed by actually standing the container up and
completing the pairing step for real. If the credential-store workaround or the
loopback networking turns out more fragile in a container than assumed here,
that is worth finding out now.

## Consequences

- **Isolation.** A misbehaving or compromised bridge process is contained to
  its own image and network namespace, not running with whatever access the
  host user account has.
- **Reproducibility.** Rebuilding the mini PC means re-running one image, not
  re-deriving a systemd unit and a keychain workaround by hand from memory or
  from this ADR.
- **Neither real cost goes away.** The interactive pairing step and the
  headless-credential-store workaround are inherent to the bridge itself, not
  to how it's packaged — a container relocates them, it doesn't remove them.
  Still worth expecting as the early-friction point ADR 0001 already flagged.
- **One more image to build and keep patched.** ADR 0001 wanted "no new
  machine to patch" — this doesn't add a machine, but it does add a service
  with its own update cadence, the same cost n8n already pays under ADR 0005.
- **The credential-store volume needs to survive backups.** Losing it means
  redoing the interactive pairing, not losing mail — the postbox itself is
  unaffected, only local reconnection has to happen again.
- **Image provenance is a real, ongoing decision, not a one-time check.** Since
  this container holds live credentials, whatever image it runs from deserves
  more scrutiny than n8n's or Dovecot's — reason enough to build it from the
  provider's own release rather than adopt a community image, even though that
  is more setup than `docker pull`.

## Alternatives considered

- **A community-maintained prebuilt image.** Faster to stand up, no Dockerfile
  to maintain. Rejected for now: it's unofficial, and this is the one
  component holding live mail credentials. Worth revisiting if a specific
  image earns enough trust — an auditable Dockerfile, a binary sourced from
  the provider's own release, active maintenance — to be worth the
  convenience.
- **Run it directly as a systemd service on the host**, per ADR 0001's
  original wording. Fewer moving parts, no image to build. Rejected: loses the
  isolation and reproducibility a container gives a credential-holding
  process, and removes neither of the two real costs (pairing, keychain
  workaround) that this ADR actually turns on.
- **Reach the postbox some other way, without a bridge.** Not available — this
  postbox is only reachable over IMAP through its own bridge process, which is
  not something this project controls.
