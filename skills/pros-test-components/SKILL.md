---
name: pros-test-components
description: Manual command. Run only when the user explicitly types it. Runs React Native component tests with Testing Library.
argument-hint: "[test file or pattern]"
disable-model-invocation: true
---

# Run component tests

Tests: $ARGUMENTS

1. Confirm `@testing-library/react-native` is in `package.json` and find its test script. If it's missing, say so and stop. Don't install anything.
2. Run only the component tests through the project's script or `npx jest $ARGUMENTS`. Use the narrowest scope that covers the request.
3. Report the exact command, exit code, and passed, failed and skipped counts. Show only the first useful lines of each failure.

Don't fix failures unless asked. If it didn't run, say "not run" and why.
