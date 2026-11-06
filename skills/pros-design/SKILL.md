---
name: pros-design
description: Manual command. Run only when the user explicitly types it. Applies the right UI design guidance for web or mobile.
argument-hint: "<what to design>"
disable-model-invocation: true
---

# Design UI

Request: $ARGUMENTS

Check the project type:

- **React Native or Expo** (`react-native` or `expo` in `package.json`): use the `mobile-design` skill.
- **Web**: use the `hallmark` skill. It starts on an existing design only if the user names Hallmark or asks for a redesign.
- **Both**: ask which one this request is for.

Use Hallmark's static lint only. Don't run `sloplint --render`, take screenshots or open a browser unless the user asks.
