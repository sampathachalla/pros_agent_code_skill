---
name: pros-tokens
description: Manual command. Run only when the user explicitly types it. Reports token usage from local session logs.
argument-hint: "[claude|codex|cursor|antigravity]"
disable-model-invocation: true
---

# Report token usage

Agent: $ARGUMENTS (default: the agent you are running in)

1. Run `~/.pros-toolkit/bin/pros tokens --agent <agent>`. On Windows, use `pros tokens --agent <agent>`.
2. Summarize input, output and cache tokens, estimated cost, the current session, and the most expensive activities and skills.
3. Say that token counts are recorded locally and that costs are API-price estimates, not a bill.

Note that this report adds to the conversation. The user can run the same command in a terminal for free.
