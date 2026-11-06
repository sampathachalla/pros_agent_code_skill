---
name: pros-review
description: Manual command. Run only when the user explicitly types it. Reviews changed code with Ponytail.
argument-hint: "[base branch, commit or path]"
disable-model-invocation: true
---

# Review changes

Target: $ARGUMENTS

1. Read `~/.pros-toolkit/upstream/ponytail-review/SKILL.md` and follow its review method.
2. Work out the scope, in this order: the target above, staged and unstaged changes, or the last commit. Start from `git diff`, then read only the connected code you need. Don't load the whole repo.
3. Report potential bugs, security concerns and unnecessary changes, ranked by severity, with file and line.

Report only. Don't change code or run tests unless the user asks.
