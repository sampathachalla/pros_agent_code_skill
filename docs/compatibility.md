# Compatibility and limits

Checked on 2026-11-06.

## Integrations

| Tool | Pin | Scope | How it's used |
|---|---|---|---|
| GitHub Spec Kit | `specify-cli` 1.3.2 | CLI global, setup per project | Installed with `uv`. Runs in a repo only on request. |
| Graphify | `graphifyy` 0.9.103 | CLI global, index per project | Installed with `uv`. `graphify install` isn't run because it adds an always-on block and a hook. |
| Karpathy Skills | `2c60614` | Global skill | Fetched at install. The repo has no LICENSE file, though its README says MIT. |
| Anthropic Skills | `2c5958e` | Global skills | `mcp-builder` and `skill-creator` only. `webapp-testing` is left out because it can drive browsers. |
| Ponytail | v5.3.3 | Files used by commands | Review and audit instructions only, not registered as skills, so they run only on request. Its plugin and hooks aren't installed. |
| Hallmark | `407fa68` | Global skill, web only | `puppeteer-core` isn't installed, so its browser checks skip. Its image generation needs your own `TOGETHER_API_KEY`. Photo saving downloads from Wikimedia Commons. |
| Playwright | Per project | Dev dependency | Run through `pros-test-web`. |
| Maestro | 2.12.1 | Global CLI, optional | Zip verified by SHA-256. Run through a wrapper that opts out of analytics. |
| React Native Testing Library | Per project | Dev dependency | Run through `pros-test-components`. |
| token-usage | v0.9.0 | Local script | Only `token_usage.py` and its pricing data. No plugin or hooks. It's a small project, so it was scanned for network use, and none was found. |
| ccusage | 20.0.48 | `npx` | Run with `--offline`. Has no Cursor report. |

`uv tool install` pins these packages, not their dependencies. `npx` downloads `ccusage` on first use.

## Agents

| | Skills folder | Rules | Test prompts |
|---|---|---|---|
| Claude Code | `~/.claude/skills` | Block in `~/.claude/CLAUDE.md` | `permissions.ask` in `~/.claude/settings.json` |
| Codex | `~/.agents/skills` | Block in `~/.codex/AGENTS.md` | `~/.codex/rules/pros-toolkit.rules` |
| Cursor | `~/.agents/skills` (also reads `~/.claude/skills`) | `pros init` per repo | None found |
| Antigravity | `~/.gemini/config/skills` | `~/.gemini/config/rules/pros-toolkit.md` | `~/.gemini/antigravity-cli/settings.json`, only if `agy` is set up |

Gemini CLI isn't supported as a separate agent. Google is moving users to Antigravity, and the Antigravity paths above cover both the app and CLI.

## Known limits

- **Rules are text patterns.** A wrapper script or custom script name can avoid a prompt. Claude Code catches `npm run test:unit`; Codex and `agy` need exact words, so they don't.
- **Existing Codex approvals are overridden.** When Codex rules conflict, the strictest wins, so `npm test` prompts even if you previously allowed it. Rules for names like `npm run test:live:auth` stay as they were.
- **Antigravity has no documented way to stop a skill activating on its own.** Manual commands say so in their description, which is a request and not a guarantee.
- **Cursor may list a skill twice,** because it reads both `~/.claude/skills` and `~/.agents/skills`. This hasn't been checked in Cursor.
- **A Cursor bug is reported** where `disable-model-invocation` is ignored in `.agents/skills`.
- **A Maestro you installed yourself** doesn't use the wrapper. Set `MAESTRO_CLI_NO_ANALYTICS=1`.
