# Pros Agent Code Skill

One global setup for coding agents. Install it once and Claude Code, Codex, Cursor and Antigravity share the same commands, skills and rules in every project.

It aims to keep changes small, use fewer tokens, run tests only when you ask, and show where your tokens go.

## Install

You need `git` and Python 3.9 or newer. `uv` installs Graphify and Spec Kit, and Node.js runs `ccusage`.

```sh
git clone https://github.com/sampathachalla/pros_agent_code_skill.git
cd pros_agent_code_skill
./scripts/install.sh --dry-run     # preview every change
./scripts/install.sh               # shows the changes and asks first
pros doctor                        # verify
```

Add `--with-maestro` if you build mobile apps. On Windows, run `scripts\install.ps1` (not yet tested on Windows).

The installer finds your agents and needs no admin rights. If `pros` isn't found afterwards, add `~/.local/bin` to your `PATH`.

## Commands

Use `/pros-plan` in Claude Code, Cursor and Antigravity, or `$pros-plan` in Codex.

| Command | What it does |
|---|---|
| `pros-plan` | Plan a feature without changing code. Uses Spec Kit if you ask for a spec. |
| `pros-implement` | Make the smallest change that solves the task. |
| `pros-review` | Review changed files with Ponytail. Report only. |
| `pros-audit` | Audit the repository with Ponytail. Report only. |
| `pros-design` | Apply Hallmark on web, or mobile design guidance on React Native. |
| `pros-graph` | Inspect code relationships with Graphify. |
| `pros-test-web` | Run Playwright. |
| `pros-test-mobile` | Run Maestro. |
| `pros-test-components` | Run React Native Testing Library tests. |
| `pros-tokens` | Report token usage. |

The `pros-` prefix keeps your built-in `/plan`, `/review` and `/design` working.

These skills can also activate on their own when relevant: `karpathy-guidelines` (coding), `pros-graph` (large repo exploration), `hallmark` (new web pages), `mobile-design` (React Native), `mcp-builder` and `skill-creator`. Only short descriptions load until a skill is used.

## Terminal commands

```sh
pros doctor                  # check the installation
pros update                  # git pull, then reinstall
pros tokens                  # token report with no LLM calls
pros init                    # add always-on Cursor rules to the current repo
pros uninstall               # reverse the install
```

## New and existing projects

Nothing is needed per project: skills are global, so they work in every repo.

The one exception is Cursor, which keeps global rules in its settings UI. Run `pros init` in a repo and commit `.cursor/rules/pros-toolkit.mdc` to give that repo always-on rules.

## What each agent supports

| | Claude Code | Codex | Cursor | Antigravity |
|---|---|---|---|---|
| Global skills | Yes | Yes | Yes | Yes |
| Global rules | Yes | Yes | **`pros init` per repo** | Yes |
| Manual-only commands | Enforced | Enforced | Enforced (reported bug in `.agents/skills`) | **Instructions only** |
| Test blocking | Enforced | Enforced | **Instructions only** | Enforced in `agy`; **instructions only** in the app and IDE |

"Enforced" means the agent itself asks before running a matched command. "Instructions only" means the agent is told the rule but nothing stops it.

Enforcement matches command text, so it can be missed. A script that calls Playwright internally isn't caught, and Codex and `agy` don't catch `npm run test:unit`. See [docs/compatibility.md](docs/compatibility.md).

## Safety

- Every upstream skill is pinned to a commit and verified by hash in [toolkit.lock.json](toolkit.lock.json). No remote install scripts run.
- Existing configs are never changed without showing a diff and asking first.
- Your own text stays outside a marked block, and a skill that already exists is left alone.
- No hooks, background services or MCP servers are installed.
- `pros uninstall` restores configs to their exact previous bytes. If you edited one since, only the toolkit's entries are removed.
- Reports run locally, and the Maestro install opts out of its analytics.

## Not included yet

- MCP setup. `doctor` only reports whether `graphify-mcp` is available.
- Windows testing.
- Dedicated `coding` and `backend-development` skills. The rules and `karpathy-guidelines` cover these for now.
- Measured token savings. Upstream figures are the authors' own claims, so measure them with `pros tokens` and `graphify benchmark`.

## More

- [Usage guide](docs/usage.md)
- [Compatibility and limits](docs/compatibility.md)
- [Troubleshooting](docs/troubleshooting.md)

## License

MIT, for this repository's own files. Upstream projects are downloaded during install, keep their own licenses, and aren't redistributed here.
