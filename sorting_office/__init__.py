"""Sorting Office — collecting newsletter mail and deciding how long to keep it.

This package holds the decisions the pipeline makes, deliberately kept apart from
the machinery that carries them out. Nothing here talks to a mailbox, a rule
store or n8n: a message is described by its metadata, and every function is a
pure decision over that metadata.

That split is what makes the plain-English scenarios in ``openspec/specs/``
testable without any of the infrastructure existing yet, and it is what keeps
[ADR 0005](../docs/decisions/0005-n8n-execution-engine.md) genuinely provisional.
"""
