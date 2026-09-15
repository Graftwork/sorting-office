#!/bin/sh
set -eu

# Everything the bridge keeps between runs — its own account/vault config
# and cache, not just the keyring secret — lives under one mounted home
# directory. A keyring-only mount looked sufficient but wasn't: the app's
# own state sat outside it, under its own cache directory elsewhere in the
# home directory, so a container recreation silently discarded a completed
# pairing while leaving the keyring itself intact.
: "${BRIDGE_KEYRING_PASSPHRASE:?BRIDGE_KEYRING_PASSPHRASE must be set}"
export HOME=/data
mkdir -p "$HOME"

eval "$(dbus-launch --sh-syntax)"
export DBUS_SESSION_BUS_ADDRESS DBUS_SESSION_BUS_PID
eval "$(printf '%s\n' "$BRIDGE_KEYRING_PASSPHRASE" | gnome-keyring-daemon --unlock --components=secrets)"
export GNOME_KEYRING_CONTROL SSH_AUTH_SOCK

# The bridge binary and its flags are the provider's, supplied at deploy
# time (CMD/args on `docker run`), not named in this script (ADR 0009).
exec "$@"
