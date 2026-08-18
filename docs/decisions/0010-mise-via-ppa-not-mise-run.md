# ADR 0010: Install mise via its Ubuntu PPA, not the mise.run installer

- **Status:** accepted
- **Date:** 2026-08-18

## Context

[Stock ADR 0010](stock-0010-cloud-environment-setup-script.md) shipped a
cloud-environment setup script installing mise via `curl https://mise.run |
sh`, with one thing explicitly flagged as unverified: whether the install
completes once `mise.run` itself is reachable. No session available to that
ADR's author could test past the point where the domain was blocked.

This project created the actual Custom environment and tried it for real.
Measured, not guessed — the setup script's own output:

```
100 12418  100 12418    0     0  48522      0 --:--:-- --:--:-- --:--:--     0
mise: installing mise...
curl: (22) The requested URL returned error: 403
```

`mise.run` itself downloaded cleanly (12418 bytes, the install script). The
failure is one level in: that script's own attempt to fetch the actual mise
binary. mise's installer pulls that from a GitHub release asset, and this
matches exactly what an earlier investigation on this project found and
documented: cloud sessions' GitHub proxy restricts release-asset requests to
repositories attached to the session, and `jdx/mise` is not one. Adding
`mise.run` to a Custom environment's allowed domains was necessary but not
sufficient — it gets the installer running, and the installer then hits a
wall that no amount of domain-allowlisting reaches, because the restriction
is about repository attachment, not network access level.

## Decision

Install mise from its Ubuntu PPA instead:

```bash
apt-get update
apt-get install -y software-properties-common
add-apt-repository -y ppa:jdxcode/mise
apt-get update
apt-get install -y mise
```

This never touches GitHub. `launchpad.net` and `ppa.launchpad.net` are
already on a Trusted environment's default allowlist — confirmed against
Anthropic's own documented list, not assumed — so this route may not need a
Custom environment's domain configuration at all. Untested past that point in
this project specifically, since the environment already in use is Custom
from the `mise.run` era; worth someone trying Trusted alone the next time a
fresh environment is set up.

## Consequences

- The manual step Stock ADR 0010 already named — pasting a script into a
  Custom environment's Setup Script field, once per account — still applies.
  This changes what gets pasted, not whether a human still has to paste it.
- **Lost: version pinning.** Stock's script pinned `MISE_VERSION` deliberately,
  consistent with `mise.toml` pinning everything else mise manages. `apt-get
  install -y mise` takes whatever the PPA currently carries. Pinning through
  apt is possible (`mise=<version>`) but needs the PPA's actual version
  strings in hand to do correctly, which nobody has checked yet. Recorded as
  an open gap, not silently dropped.
- **Confirms, for real, the thing Stock's ADR left open.** Stock's own
  script was never actually shown to fail — only shown to be untestable from
  inside any available session. This project is the first place that
  changed, and the finding belongs upstream: Stock's script will fail the
  same way for the next project that tries it, for the same reason.

## Alternatives considered

- **Keep `curl https://mise.run | sh` and also attach `jdx/mise` to the
  session somehow**, to route around the repo-scoping restriction directly.
  Not pursued — "attached repository" is a property of what a coding session
  is working on, not something a cloud environment's setup script appears
  able to declare for itself, and reaching for a workaround to a restriction
  that exists on purpose felt like the wrong instinct compared to using
  infrastructure that was never subject to it in the first place.
- **A version-pinned apt install, guessing at the PPA's revision string.**
  Rejected: a wrong guess fails the install outright, which is worse than an
  honestly-flagged gap in an install that otherwise works.
