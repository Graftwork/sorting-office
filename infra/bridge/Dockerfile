# The postbox's local bridge (ADR 0001, ADR 0012). Some providers only expose
# IMAP through their own bridge process, run headless here; which provider,
# and its package, are deployment configuration for the mini PC — this
# codebase doesn't name either (ADR 0009). The .deb is supplied at build
# time; nothing about it is baked into this image or committed to the repo.
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates dbus-x11 gnome-keyring \
    && rm -rf /var/lib/apt/lists/*

ARG BRIDGE_DEB
COPY ${BRIDGE_DEB} /tmp/bridge.deb
RUN apt-get update \
    && apt-get install -y --no-install-recommends /tmp/bridge.deb \
    && rm -rf /var/lib/apt/lists/* /tmp/bridge.deb

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
