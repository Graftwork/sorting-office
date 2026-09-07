# The local mailbox (ADR 0003): a real IMAP server, IMAP only.
# No SMTP receiving, no submission, no LMTP — deliberately absent, not just
# unconfigured, so there is no listener to lock down later.
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends dovecot-imapd \
    && rm -rf /var/lib/apt/lists/*

COPY local.conf /etc/dovecot/local.conf

RUN mkdir -p /var/mail/vhosts \
    && groupadd -g 5000 vmail \
    && useradd -g vmail -u 5000 vmail -d /var/mail/vhosts -m \
    && chown -R vmail:vmail /var/mail/vhosts

EXPOSE 143
CMD ["dovecot", "-F"]
