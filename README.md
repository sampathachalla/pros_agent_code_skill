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

The `pros-` commands and skills are global, so they work in every repo with no setup.

### Per-repo setup

Run these once in each repo, from the repo folder. All of them are optional, so use only the ones you need.

```sh
# Spec Kit: adds the /speckit- commands to this repo.
# Use codex, cursor-agent or agy instead of claude for other agents.
specify init --here --integration claude

# Cursor only: adds always-on rules, because Cursor keeps global rules in its settings.
pros init

# Large repos: builds a local map of how the code connects. Uses no AI tokens.
graphify update .

# Keeps that generated map out of Git.
echo 'graphify-out/' >> .gitignore
```

| Command | Use it when | What it does |
|---|---|---|
| `specify init --here --integration claude` | You want Spec Kit in this repo | Adds Spec Kit's files and commands for that agent. Run it again for each extra agent. |
| `pros init` | You use Cursor on this repo | Writes `.cursor/rules/pros-toolkit.mdc`. |
| `graphify update .` | The repo is large or unfamiliar | Builds the map that `/pros-graph` reads. Rerun it after big code changes. |
| `echo 'graphify-out/' >> .gitignore` | You built a graph | Stops Git committing the generated map. Run it once. |

Commit the new files so they go up with your next push, then restart your agent in that repo. Teammates who pull the repo get the Spec Kit commands for that agent without running `specify init`.

### Spec Kit commands

Spec Kit needs the `specify init` step above. After that, type these directly in your agent, one at a time, and review each result. In Codex, use `$` instead of `/`.

| Command | Use it to | Example |
|---|---|---|
| `/speckit-constitution` | Set project-wide principles. Run once per project. | `/speckit-constitution Focus on fast pages, accessibility and simple code` |
| `/speckit-specify` | Describe what to build and why. | `/speckit-specify A home page with a hero, features and a sign-up button` |
| `/speckit-clarify` | Optional. Answer up to 5 questions that fill gaps in the spec. | `/speckit-clarify` |
| `/speckit-plan` | Choose how to build it. | `/speckit-plan Use Next.js and our existing components` |
| `/speckit-checklist` | Optional. Create a quality checklist for the requirements. | `/speckit-checklist` |
| `/speckit-tasks` | Break the plan into ordered tasks. | `/speckit-tasks` |
| `/speckit-analyze` | Optional. Check that the spec, plan and tasks agree. | `/speckit-analyze` |
| `/speckit-implement` | Build the code from the tasks. | `/speckit-implement` |
| `/speckit-converge` | Compare the code with the spec and add tasks for anything unbuilt. | `/speckit-converge` |

The shortest path is `specify`, `plan`, `tasks`, `implement`, `converge`. Repeat `implement` and `converge` until converge reports `Converged`. Spec Kit uses more tokens than a normal request, so keep it for bigger features and use `/pros-implement` for small changes.

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
