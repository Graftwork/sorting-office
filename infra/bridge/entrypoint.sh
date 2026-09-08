#!/bin/sh
set -eu

# Filesystem-backed credential store standing in for the desktop secret
# service the bridge expects by default (ADR 0012): a keyring file on the
# mounted data volume, unlocked at startup with a passphrase supplied by the
# deployment — never baked into this image.
: "${BRIDGE_KEYRING_PASSPHRASE:?BRIDGE_KEYRING_PASSPHRASE must be set}"
export XDG_DATA_HOME=/data/keyrings
mkdir -p "$XDG_DATA_HOME"

eval "$(dbus-launch --sh-syntax)"
export DBUS_SESSION_BUS_ADDRESS DBUS_SESSION_BUS_PID
eval "$(printf '%s\n' "$BRIDGE_KEYRING_PASSPHRASE" | gnome-keyring-daemon --unlock --components=secrets)"
export GNOME_KEYRING_CONTROL SSH_AUTH_SOCK

# The bridge binary and its flags are the provider's, supplied at deploy
# time (CMD/args on `docker run`), not named in this script (ADR 0009).
exec "$@"
