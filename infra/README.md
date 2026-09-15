# Deploying to the mini PC

The mini PC is reachable only over Tailscale (ADR 0001) — everything here is
run from a machine already on that tailnet, over SSH, never from anywhere else.
Nothing here is provider-specific: which bridge package to use, and the real
credentials both containers need, are deployment configuration you supply on
the mini PC itself, not something this repo knows about (ADR 0009).

This covers what's built so far: the local mailbox (Dovecot) and the postbox's
bridge container. It does not yet cover n8n (task 1.4) — that gets added here
once it exists.

## Once, on a fresh mini PC

Runtime is Podman, rootless, via the `podman-docker` compatibility shim — every
`docker` command below is really running `podman` (`/usr/bin/docker` is a
one-line script that execs it). Chosen over Docker's own daemon deliberately:
rootless means the bridge — the one container holding live mail credentials
(ADR 0012) — never runs as a process with root's own privileges on the host.

```bash
sudo apt install podman-docker
```

Two things that follow from rootless specifically, not from Podman in general:

- **Port 143 needs a remap.** A rootless container can't bind a port below
  1024 on the host — confirmed directly (`bind(0.0.0.0, 143) failed:
  Permission denied`), not assumed. Map Dovecot's container-side 143 to a
  host-side port above 1024 instead (1144 is used below, distinct from the
  bridge's own 1143) — that's the host port IMAP clients connect to.
- **`--restart unless-stopped` needs linger to survive a reboot**, since a
  rootless container is a process owned by your user's session, and without
  it the session (and everything in it) doesn't start until that user logs
  in:

  ```bash
  loginctl enable-linger "$(whoami)"
  ```

  This part isn't re-verified end-to-end against an actual reboot below — it's
  documented Podman behaviour, not something tested in this pass. Worth
  confirming for real once both containers are up: reboot the mini PC and
  check `docker ps` afterwards without logging in and starting anything by
  hand.

Also needed:

- Tailscale installed and joined to the tailnet (already true per ADR 0001 —
  pi-hole depends on it).
- This repo cloned somewhere durable, e.g. `$HOME/sorting-office`.

Find the tailnet address everything below binds to, and keep it handy:

```bash
tailscale ip -4
```

Both containers bind to this address specifically — never `0.0.0.0` — so nothing
here is reachable outside the tailnet even if the mini PC's other interfaces are
less trusted.

## The local mailbox (Dovecot)

```bash
cd $HOME/sorting-office/infra/dovecot
docker build -t sorting-office-dovecot .

# Real users, not the test fixture from the repo's own verification pass.
# scheme=CRYPT in local.conf accepts SHA-512 crypt ($6$) hashes.
mkdir -p $HOME/sorting-office/data/dovecot
printf 'sweeper:%s\n' "$(openssl passwd -6)" > $HOME/sorting-office/data/dovecot/users
mkdir -p $HOME/sorting-office/data/dovecot/mail

docker run -d --name sorting-office-dovecot \
  --restart unless-stopped \
  -p "$(tailscale ip -4)":1144:143 \
  -v $HOME/sorting-office/data/dovecot/users:/etc/dovecot/users:ro \
  -v $HOME/sorting-office/data/dovecot/mail:/var/mail/vhosts \
  sorting-office-dovecot
```

Host-side port is 1144, not 143 — rootless can't bind the privileged port
directly (see above), and 1143 is already the bridge's port below. Dovecot
inside the container still listens on 143; only the host-side mapping moves.
Point IMAP clients at `<tailnet address>:1144`.

The mail volume has to be a host path, not left as the container's writable
layer — otherwise `docker rm` (a rebuild, a crash recovery) silently empties
the mailbox retention depends on.

Confirm it's actually serving, not just running — verified for real, end to
end, against this exact image under rootless Podman: LOGIN succeeded and
`LIST "" *` returned `INBOX`. Repeat the same check here:

```bash
curl -v --url "imap://$(tailscale ip -4):1144/" -u sweeper:<password>
```

## The postbox's bridge

No official container image exists for this (ADR 0012), and this repo doesn't
know which provider you're bridging to — get that provider's own official
`.deb` onto the mini PC yourself, from their own release channel.

```bash
cd $HOME/sorting-office/infra/bridge
cp /path/to/the/providers/release.deb ./bridge.deb
docker build --build-arg BRIDGE_DEB=bridge.deb -t sorting-office-bridge .
rm bridge.deb   # only ever a local build input, never committed

mkdir -p $HOME/sorting-office/data/bridge
```

The volume mounts at `/data`, and the container's entrypoint points `HOME`
there — not just the keyring's own storage. Found the hard way: an earlier
version of this only redirected the keyring, and the bridge's own account
config and cache turned out to live elsewhere under `$HOME`, outside that
mount. A container recreation silently discarded a completed pairing while
leaving the keyring itself intact — `list` reported no active accounts after
a `docker rm`/`docker run` against a volume that visibly still had content.
Redirecting the whole home directory means whatever the app decides to
persist, wherever it puts it, ends up under the one mounted path.

**One-time interactive pairing** — nothing committed to this repo can do this
step unassisted (ADR 0012); it needs you, present, with the account's password
and second factor. Run it attached, in the foreground, not detached, so you
can actually drive the login:

```bash
docker run -it --name sorting-office-bridge \
  -e BRIDGE_KEYRING_PASSPHRASE=<a passphrase you choose, kept off this repo> \
  -v $HOME/sorting-office/data/bridge:/data \
  -p "$(tailscale ip -4)":1143:1143 \
  sorting-office-bridge \
  <the provider's bridge binary and flags for headless/CLI mode>
```

Follow that shell's own login flow — `help` lists the actual command names
rather than guessing them. Once paired, exit the shell (this stops the
container; that's fine, the pairing lives in the volume, not the container)
and start the real persistent one from the same volume:

```bash
docker rm sorting-office-bridge
docker run -d -i --name sorting-office-bridge \
  --restart unless-stopped \
  -e BRIDGE_KEYRING_PASSPHRASE=<the same passphrase as the pairing run> \
  -v $HOME/sorting-office/data/bridge:/data \
  -p "$(tailscale ip -4)":1143:1143 \
  sorting-office-bridge \
  <the provider's bridge binary and flags for headless/CLI mode>
```

`-i` matters even though this is detached (`-d`): without it, the CLI's own
shell hits EOF immediately on the closed stdin and the container exits right
after printing its banner. `--restart unless-stopped` means a dropped session
or a transient crash doesn't take it down for good — Podman brings it back
rather than it sitting dead until someone notices. The credential lives in
the mounted volume and survives every restart or recreation from here on —
the container's own entrypoint re-unlocks it with `BRIDGE_KEYRING_PASSPHRASE`
on every start, no re-pairing needed unless that volume is lost.

Confirm the bridge is actually serving IMAP post-pairing the same way as
Dovecot above — `curl imap://` against its bound address and port, real LOGIN,
real LIST.

## Confirming tailnet-only reachability (task 1.3)

From a machine *not* on the tailnet, both of the above should be entirely
unreachable. From a tailnet machine, both should answer only on the tailnet
address, never on the mini PC's LAN or public interface if it has one:

```bash
# From the mini PC itself — should show only the tailnet address bound, not 0.0.0.0
docker ps --format '{{.Names}}: {{.Ports}}'
```
