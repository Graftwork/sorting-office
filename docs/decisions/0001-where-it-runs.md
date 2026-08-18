# ADR 0001: It runs on the always-on mini PC, reachable only over Tailscale

- **Status:** accepted
- **Date:** 2026-08-12
- **Carried forward:** written before this repository was rebuilt, and renumbered
  on the way in. The reasoning is unchanged; the mail provider it originally
  named has been replaced by *the postbox*, per
  [ADR 0009](0009-provider-agnostic-collection.md).

## Context

The pipeline has to run on a schedule, unattended, to be any use — mail
accumulates whether or not a machine happens to be awake. That rules out the
desktop, which is off most of the time and power-hungry when it isn't.

Standing up a new headless server just for this is disproportionate to the
problem, and adds a machine to maintain.

There is already an always-on Linux mini PC running pi-hole: low power, already
trusted with a background service, already on the network.

## Decision

Run on the existing mini PC. Anything the postbox needs in order to expose IMAP —
some providers only do so through a local bridge process — runs there headless,
as a systemd service.

Access is LAN/Tailscale only. Tailscale is already set up and in use for
pi-hole. Nothing is exposed to the public internet — no port forwarding, no
reverse proxy, no public DNS.

## Consequences

- No new hardware and no new machine to patch.
- A headless bridge is new territory, where the postbox needs one. Such tools are
  usually GUI-oriented by default, so running one as a service needs deliberate
  setup and is a likely source of early friction. Worth expecting rather than
  being surprised by.
- The Counter (admin UI) is only reachable from the tailnet. That is a feature:
  an interface onto unencrypted mail should not be internet-facing.
- If this ever moves to a cloud VM — DigitalOcean, for preference — joining that
  VM to the same tailnet preserves the identical private-access model, so the
  decision does not paint us into a corner.
- The mini PC becomes a single point of failure for mail pruning. Acceptable:
  the failure mode is "mail stops being pruned", which is the status quo, not
  data loss.

## Alternatives considered

- **The desktop.** Off most of the time; the schedule would be unreliable.
- **A new headless server.** Disproportionate, and another machine to maintain.
- **A cloud VM from the start.** Puts unencrypted mail and postbox credentials on
  someone else's hardware for no benefit while a perfectly good always-on
  machine sits on the LAN.
