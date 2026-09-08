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

- Docker installed, and enabled to start on boot (`systemctl enable --now
  docker` — most distros already do this by default; confirm rather than
  assume).
- Tailscale installed and joined to the tailnet (already true per ADR 0001 —
  pi-hole depends on it).
- This repo cloned somewhere durable, e.g. `/opt/sorting-office`.

Find the tailnet address everything below binds to, and keep it handy:

```bash
tailscale ip -4
```

Both containers bind to this address specifically — never `0.0.0.0` — so nothing
here is reachable outside the tailnet even if the mini PC's other interfaces are
less trusted.

## The local mailbox (Dovecot)

```bash
cd /opt/sorting-office/infra/dovecot
docker build -t sorting-office-dovecot .

# Real users, not the test fixture from the repo's own verification pass.
# scheme=CRYPT in local.conf accepts SHA-512 crypt ($6$) hashes.
mkdir -p /opt/sorting-office/data/dovecot
printf 'sweeper:%s\n' "$(openssl passwd -6)" > /opt/sorting-office/data/dovecot/users
mkdir -p /opt/sorting-office/data/dovecot/mail

docker run -d --name sorting-office-dovecot \
  --restart unless-stopped \
  -p "$(tailscale ip -4)":143:143 \
  -v /opt/sorting-office/data/dovecot/users:/etc/dovecot/users:ro \
  -v /opt/sorting-office/data/dovecot/mail:/var/mail/vhosts \
  sorting-office-dovecot
```

The mail volume has to be a host path, not left as the container's writable
layer — otherwise `docker rm` (a rebuild, a crash recovery) silently empties
the mailbox retention depends on.

Confirm it's actually serving, not just running (same check used to verify the
image itself — see the repo's commit history for `infra/dovecot`):

```bash
curl -v --url "imap://$(tailscale ip -4)/" -u sweeper:<password>
```

LOGIN should succeed and `LIST "" *` should return `INBOX`.

## The postbox's bridge

No official container image exists for this (ADR 0012), and this repo doesn't
know which provider you're bridging to — get that provider's own official
`.deb` onto the mini PC yourself, from their own release channel.

```bash
cd /opt/sorting-office/infra/bridge
cp /path/to/the/providers/release.deb ./bridge.deb
docker build --build-arg BRIDGE_DEB=bridge.deb -t sorting-office-bridge .
rm bridge.deb   # only ever a local build input, never committed

mkdir -p /opt/sorting-office/data/bridge

docker run -d --name sorting-office-bridge \
  --restart unless-stopped \
  -e BRIDGE_KEYRING_PASSPHRASE=<a passphrase you choose, kept off this repo> \
  -v /opt/sorting-office/data/bridge:/data/keyrings \
  -p "$(tailscale ip -4)":1143:1143 \
  sorting-office-bridge \
  <the provider's bridge binary and flags for headless/CLI mode>
```

The keyring volume is a host path for the same reason the mailbox is: losing it
means redoing the pairing below, not losing mail, but it's still avoidable.

**One-time interactive pairing** — nothing committed to this repo can do this
step unassisted (ADR 0012); it needs you, present, with the account's password
and second factor:

```bash
docker exec -it sorting-office-bridge <the provider's bridge binary> --cli
```

Follow that shell's own login flow. Once paired, the credential lives in the
mounted keyring volume and survives `docker restart` — the container's own
entrypoint re-unlocks it with `BRIDGE_KEYRING_PASSPHRASE` on every start, no
re-pairing needed unless that volume is lost.

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
