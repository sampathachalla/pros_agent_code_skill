---
name: pros-audit
description: Manual command. Run only when the user explicitly types it. Audits a whole repository with Ponytail.
argument-hint: "[path]"
disable-model-invocation: true
---

# Audit the repository

Target: $ARGUMENTS

1. Read `~/.pros-toolkit/upstream/ponytail-audit/SKILL.md` and follow its audit method.
2. Map entry points and data flow first. Use pros-graph if `graphify-out/graph.json` exists.
3. Rank findings and say what to fix first.

Report only. Don't change code or run tests unless the user asks.
