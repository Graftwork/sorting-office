# ADR 0010: Install mise unpinned, via mise.run

- **Status:** accepted
- **Date:** 2026-08-18

## Context

[Stock ADR 0010](stock-0010-cloud-environment-setup-script.md) shipped a
cloud-environment setup script installing mise via `curl https://mise.run |
sh`, pinned to a specific version, with one thing explicitly flagged as
unverified: whether the install completes once `mise.run` itself is
reachable. No session available to that ADR's author could test past the
point where the domain was blocked.

This project created the actual Custom environment and tried it for real.
Measured, not guessed — the setup script's own output:

```
mise: installing mise...
curl: (22) The requested URL returned error: 403
```

`mise.run` downloaded cleanly; the failure was one level in, in that
script's own attempt to fetch the mise binary — from a GitHub release
asset, which this session's GitHub proxy 403s because release-asset
requests are scoped to repositories attached to the session, and
`jdx/mise` isn't one.

Reading `mise.run`'s actual installer explained why, precisely — not a
guess. It picks a download host by comparing the requested version against
a `current_version` literal baked into whatever copy of the script
`mise.run` is currently serving:

```sh
if [ "$version" != "$current_version" ] || [ "$install_from_github" = "1" ]; then
  tarball_url="https://github.com/jdx/mise/releases/download/v${version}/..."
elif [ -n "${MISE_TARBALL_URL-}" ]; then
  tarball_url="$MISE_TARBALL_URL"
else
  tarball_url="https://mise.jdx.dev/v${version}/..."
fi
```

Stock's pin (`2026.8.8`) matched `current_version` when the ADR was written.
`mise.run` regenerates that literal every time mise ships a release, and
mise ships often. By the time the script actually ran, the pin no longer
matched, and the installer silently fell onto the GitHub branch — a
staleness failure, not a one-off.

A second branch, in the checksum step, makes this harder to route around
than it first looks: it runs the identical `version == current_version`
check, independently, and has no non-GitHub fallback for a version that
fails it — a matching version gets a checksum baked statically into the
script itself, a non-matching one is verified against a `SHASUMS256.txt`
fetched from GitHub, full stop. So even a `MISE_TARBALL_URL` override
pointed at `mise.jdx.dev` for a specific pinned version — untested, since
`mise.jdx.dev` is unreachable from every session available to check this
from, the same as `mise.run` originally was — would still send checksum
verification to GitHub for anything but the current version. Skipping
verification to avoid that would mean running an unverified binary as
root, trading away a real safety property to dodge a proxy restriction.

**mise's own documentation argues against pinning mise itself, directly:**

> Projects and organizations should generally set a `min_version` when they
> need a newer mise feature instead of locking every user to a specific mise
> executable. ... Pinning mise back is like preventing `apt update` or
> `brew update` from refreshing package metadata: it can hide deprecation
> messages and cause bit rot with upstream integrations like aqua-registry.

Stock's original reasoning — pin mise the same way `mise.toml` pins Python,
uv and Node — treated mise as one more managed tool. Upstream's own framing
says it isn't one: it's closer to the package manager itself, and pinning a
package manager is a known anti-pattern for the reasons quoted above, not
just a style preference.

## Decision

Don't set `MISE_VERSION`. Let the installer default to whatever version the
copy of the script it fetched considers current.

This isn't a compromise reached for lack of a working alternative — it's
what upstream recommends, and it happens to also be what keeps the
installer off GitHub permanently rather than for as long as nobody notices
the pin has gone stale. Leaving the version unset makes `version ==
current_version` true by construction, on every single run: always the
`mise.jdx.dev` tarball, always the checksum baked into that same script
copy, no network call to GitHub anywhere in the path.

A project that needs a floor on mise's own version — a feature it depends
on, say — sets `min_version` in `mise.toml`, which mise checks against
itself at run time. That's a promise about capability, not a lock on a
specific executable, and it's a separate concern from this script; not
added here since nothing currently needs one.

## Consequences

- **No pin, by design, not by omission.** The version installed will drift
  as mise ships releases, on whatever cadence the environment's cache
  rebuilds (roughly weekly, or sooner if the script or its domains change).
  Consistent with upstream's own guidance, not a corner cut.
- **Confirms, for real, the thing Stock's ADR left open** — its script does
  fail, reproducibly, the next time a pinned version goes stale. The finding
  belongs upstream in Stock, not just here.
- The environment's allowed domains need `mise.run` and `mise.jdx.dev`, not
  GitHub. Simpler than the Custom-environment domain list either earlier
  attempt needed.

## Alternatives considered

- **Keep the pin from Stock ADR 0010.** Works until mise next ships, then
  fails the same way again, silently, for the same reason — a recurring
  staleness bug rather than a fix, and now contradicted by mise's own
  guidance against pinning itself at all.
- **Install via mise's Ubuntu PPA** (`ppa:jdxcode/mise`), tried and pushed
  before this ADR reached its final form. Never touches GitHub or
  `mise.jdx.dev` at all, using `launchpad.net` — already on a Trusted
  environment's default allowlist. Reverted once the real problem turned
  out to be the stale pin rather than something inherent to `mise.run`:
  third-party Launchpad packaging depends on someone else's maintenance
  schedule, loses mise's own checksummed release artifacts, and needs its
  own from-scratch pinning story if reproducibility is ever wanted back —
  costs the original script didn't actually require paying.
- **Force `MISE_TARBALL_URL` at a pinned `mise.jdx.dev` version.** Would
  keep a specific pin if `mise.jdx.dev` serves historical versions by path,
  which could not be confirmed — blocked from testing, the same restriction
  that blocked `mise.run` originally. Even if the tarball fetch works this
  way, the checksum step has no equivalent override and would still reach
  for GitHub on anything but the current version, so this doesn't cleanly
  solve the problem it would be adopted to solve.
