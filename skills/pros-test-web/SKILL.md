---
name: pros-test-web
description: Manual command. Run only when the user explicitly types it. Runs the project's Playwright tests.
argument-hint: "[file, project or grep]"
disable-model-invocation: true
---

# Run web tests

Options: $ARGUMENTS

1. Confirm `@playwright/test` and a `playwright.config.*` exist. If not, say so and stop. Don't install anything.
2. Run through the project's package manager, for example `npx playwright test --reporter=line $ARGUMENTS`.
3. Report the exact command, exit code, and passed, failed and skipped counts. Show only the first useful lines of each failure.

Don't fix failures unless asked. If it didn't run, say "not run" and why.
