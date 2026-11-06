---
name: mobile-design
description: Design guidance for React Native and Expo screens. Use when building or changing mobile UI in a project with react-native or expo in package.json.
---

# Mobile UI design

Follow the project's theme, components and navigation first. Add no UI library without asking.

## Layout

- Respect safe areas, notches and the home indicator.
- Use one spacing scale. Build for small phones, then check large phones and tablets.
- Put primary actions within thumb reach. Use bottom sheets and native navigation patterns before custom ones.
- Keep forms clear of the keyboard, and set the right keyboard type and return key.

## Platform

- Follow each platform's conventions for navigation, back behavior and system fonts.
- Use `Platform.select` only where the platforms really differ.

## Touch and motion

- Make touch targets at least 44pt on iOS and 48dp on Android.
- Use `Pressable` with visible pressed states.
- Keep motion short and meaningful, and respect reduced motion. Use the animation library the project already has.

## States

- Design loading, empty, error and offline states for every screen that loads data.
- Use `FlatList` or the project's list component for long lists, not `ScrollView`.
- Give images fixed dimensions or an aspect ratio to prevent layout jumps.

## Accessibility

- Set `accessibilityLabel` and `accessibilityRole` on interactive elements.
- Support Dynamic Type and font scaling without clipping text.
- Meet 4.5:1 contrast for body text, in both light and dark mode.
