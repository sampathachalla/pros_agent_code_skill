# Usage guide

## Example workflows

**Build a feature:** `/pros-plan add password reset`, approve the plan, then `/pros-implement`, `/pros-review`, and `/pros-test-web` when you're ready.

**Fix a bug:** describe the bug. `karpathy-guidelines` activates on its own, or use `/pros-implement`.

**Spec-driven work:** `/pros-plan write a spec for offline sync`. Spec Kit writes into the repo, so the agent asks before running `specify init`.

**Explore a large repo:** `/pros-graph how does auth reach the database?` The first run asks before building `graphify-out/`. Add that folder to `.gitignore`.

**Design:** `/pros-design` picks Hallmark for web and `mobile-design` for React Native.

## Configure one agent

```sh
pros install --agents codex,cursor
```

Agents are normally detected from their binary, config folder or app.

## Add or remove skills

**Your own skill:** add `skills/<name>/SKILL.md`, then run `pros install`. The folder name must match the `name` field. Add `disable-model-invocation: true` to make it manual.

**A pinned upstream skill:** add an entry to `toolkit.lock.json` with an empty `tree_sha256`, run `python3 pros.py verify-pins`, copy the printed hash in, then run `pros install`. Read the skill first.

**Remove a skill:** delete its folder or lock entry, then run `pros install`.

## Update

```sh
pros update
```

This pulls the repo and reinstalls. Upstream versions change only when a commit changes `toolkit.lock.json`.

## Run tests manually

Tests never run by themselves. Use the commands below, which call the project's own Playwright, Maestro or Jest setup. Playwright and React Native Testing Library are dev dependencies in each project, so the toolkit doesn't install them.

| Command | Needs |
|---|---|
| `/pros-test-web` | `@playwright/test` and `playwright.config.*` |
| `/pros-test-mobile` | Maestro, flows in `.maestro/`, a running device |
| `/pros-test-components` | `@testing-library/react-native` |

Expect an approval prompt in Claude Code and Codex. That prompt is the enforcement working.

## Monitor token usage

```sh
pros tokens                       # Claude Code, last 7 days
pros tokens --agent codex --since 30d
pros tokens --session             # latest session only
```

The report shows input, output and cache tokens, estimated cost, session totals, activity and skill attribution, and expensive workflows. Token counts come from local logs. Costs are API-price estimates, not your subscription bill.

Run it in a terminal to avoid spending tokens. `/pros-tokens` adds the report to the conversation.

## Uninstall

```sh
pros uninstall --dry-run
pros uninstall
```

Then delete your clone. `uv` and `npm` caches stay behind and can be cleared with their own tools. Repos where you ran `pros init` keep their rule until you run `pros init --remove`.
