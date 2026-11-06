## Testing

- Never run tests on your own initiative: no Playwright, Maestro, Jest, React Native Testing Library, or full test suites.
- Don't launch browsers, emulators or visual inspection unless the user explicitly asks. This includes Hallmark `--render` checks.
- Run tests only through pros-test-web, pros-test-mobile, pros-test-components, or a direct request.
- Never report a test as passed unless it ran. Say "not run" otherwise.
