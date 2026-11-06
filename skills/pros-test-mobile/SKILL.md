---
name: pros-test-mobile
description: Manual command. Run only when the user explicitly types it. Runs the project's Maestro flows.
argument-hint: "[flow file or folder]"
disable-model-invocation: true
---

# Run mobile E2E tests

Flows: $ARGUMENTS

1. Confirm `maestro` is installed and a flow exists, usually in `.maestro/`. If not, say so and stop.
2. Check `adb devices` or `xcrun simctl list devices booted`. Ask before booting a device; don't boot one yourself.
3. If `which maestro` is not `~/.local/bin/maestro`, warn that Maestro analytics may be on and suggest setting `MAESTRO_CLI_NO_ANALYTICS=1`. Run `maestro test <flow>`, using `.maestro/` if no flow was given.
4. Report the exact command, exit code, and each flow's result. Open screenshots only for failures, and only when needed.

Don't fix failures unless asked. If it didn't run, say "not run" and why.
