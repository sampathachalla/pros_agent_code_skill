---
name: pros-implement
description: Manual command. Run only when the user explicitly types it. Implements a task with the smallest change.
argument-hint: "<task>"
disable-model-invocation: true
---

# Implement with minimal changes

Task: $ARGUMENTS

1. Read the code the change touches and trace the real flow.
2. Use the first option that works: no code needed, existing project code, standard library, platform feature, installed dependency, then new code.
3. Change only what the task requires. Keep the project's style. Add no new dependency without asking.
4. Keep validation, error handling, security and accessibility.
5. Report the files changed and any follow-ups you noticed but left alone.

Don't run tests. Say "tests not run" and suggest the right pros-test command.
