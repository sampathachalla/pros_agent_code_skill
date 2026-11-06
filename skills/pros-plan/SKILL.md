---
name: pros-plan
description: Manual command. Run only when the user explicitly types it. Plans a feature without changing code.
argument-hint: "<feature>"
disable-model-invocation: true
---

# Plan a feature

Feature: $ARGUMENTS

Make no code changes.

1. Read only the code the feature touches. Use pros-graph if `graphify-out/graph.json` exists.
2. Check what the project already has that can be reused.
3. Write the plan: goal, files to change, steps, risks, open questions, and how to verify it.
4. Keep it to the smallest design that meets the goal, then stop for approval.

## Spec Kit

Use Spec Kit only if the user asks for a spec or spec-driven development. It writes files into the repo.

1. If `.specify/` is missing, show this command and get approval: `specify init --here --integration <agent>`. Keys: `claude`, `codex`, `cursor-agent`, `agy`.
2. Follow the `speckit-*` commands it installs, one at a time, reviewing each result with the user.
