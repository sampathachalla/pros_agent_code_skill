# Pros Agent Code Skill

One global setup for coding agents. Install it once and Claude Code, Codex, Cursor and Antigravity share the same commands, skills and rules in every project.

It aims to keep changes small, use fewer tokens, run tests only when you ask, and show where your tokens go.

**Jump to:**

1. [Global installation and verification](#1-global-installation-and-verification)
2. [Commands to run in the terminal](#2-commands-to-run-in-the-terminal)
3. [Commands to run per repo](#3-commands-to-run-per-repo)
4. [Commands to run in the agent](#4-commands-to-run-in-the-agent)

## 1. Global installation and verification

Do this once per computer. You need `git` and Python 3.9 or newer. `uv` installs Graphify and Spec Kit, and Node.js runs `ccusage`.

**Install**

```sh
git clone https://github.com/sampathachalla/pros_agent_code_skill.git
cd pros_agent_code_skill
./scripts/install.sh --dry-run     # preview every change
./scripts/install.sh               # shows the changes and asks first
```

Use `./scripts/install.sh --with-maestro` to include Maestro for mobile testing. On Windows, run `scripts\install.ps1` (not yet tested on Windows).

The installer finds your agents and needs no admin rights.

**Add the tools to your PATH**

If `pros` isn't found after installing, run this and open a new terminal:

```sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zprofile
```

**Verify**

```sh
pros doctor
```

It should end with `All required checks passed.` Then restart your agents so they load the skills.

## 2. Commands to run in the terminal

Run these from any folder. They use no AI tokens.

| Command | What it does |
|---|---|
| `pros doctor` | Checks the installation |
| `pros update` | Pulls the latest toolkit and reinstalls it |
| `pros tokens` | Shows a Claude Code token report for the last 7 days |
| `pros tokens --agent codex --since 30d` | Shows a report for another agent or period. Agents: `claude`, `codex`, `cursor`, `antigravity`. |
| `pros tokens --session` | Shows the latest session only |
| `pros uninstall --dry-run` | Previews what uninstalling would change |
| `pros uninstall` | Reverses the install |

## 3. Commands to run per repo

Run these once, inside the repo folder. All of them are optional, so use only the ones you need. The `pros-` commands work in every repo without them.

**Spec Kit:** adds the `/speckit-` commands to this repo.

```sh
specify init --here --force --non-interactive --integration claude --script sh
specify integration install codex
specify integration install cursor-agent
specify integration install agy --force
```

Keep only the agents you use. `--force` and `--non-interactive` skip the confirmation prompts, and `--script sh` uses shell scripts (use `ps` on Windows). Run `specify init` once: running it again with `--force` overwrites any edits to Spec Kit's templates. Don't use it for a second agent either: it replaces your first agent instead of adding one. If your first agent's CLI isn't on your PATH, add `--ignore-agent-tools` to `specify init`.

**Cursor:** adds always-on rules, because Cursor keeps global rules in its settings.

```sh
pros init
```

**Graphify:** for large repos. Builds a local map of how the code connects and uses no AI tokens.

```sh
graphify update .
printf '\ngraphify-out/\n' >> .gitignore
```

Rerun `graphify update .` after big code changes. To confirm Git ignores the graph, run `git check-ignore graphify-out`. It should print `graphify-out`.

**Commit the new files**

```sh
git add .
git commit -m "Add agent setup"
```

Then restart your agent in that repo.

| | Commit it? | After someone pulls `main` |
|---|---|---|
| Spec Kit files | Yes | They get the commands. No need to run `specify init` again. |
| `.cursor/rules/pros-toolkit.mdc` | Yes | They get the rules. |
| `.gitignore` line | Yes | They get it. |
| `graphify-out/` | No | Each person runs `graphify update .` once. |

Spec Kit needs no `.gitignore` command. It creates its own `.specify/.gitignore` for machine-only files.

## 4. Commands to run in the agent

Type these in your agent's chat, followed by your request. In Codex, use `$` instead of `/`.

### Pros commands

These work in every repo.

| Command | What it does | Example |
|---|---|---|
| `/pros-plan` | Plans a feature without changing code. Uses Spec Kit if you ask for a spec. | `/pros-plan add password reset` |
| `/pros-implement` | Makes the smallest change that solves the task. | `/pros-implement add the reset endpoint` |
| `/pros-review` | Reviews changed files with Ponytail. Report only. | `/pros-review` |
| `/pros-audit` | Audits the repository with Ponytail. Report only. | `/pros-audit` |
| `/pros-design` | Applies Hallmark on web, or mobile design guidance on React Native. | `/pros-design a settings screen` |
| `/pros-graph` | Inspects how the code connects with Graphify. | `/pros-graph how does login reach the database?` |
| `/pros-test-web` | Runs Playwright. | `/pros-test-web` |
| `/pros-test-mobile` | Runs Maestro. | `/pros-test-mobile` |
| `/pros-test-components` | Runs React Native Testing Library tests. | `/pros-test-components` |
| `/pros-tokens` | Reports token usage. | `/pros-tokens` |

The `pros-` prefix keeps your built-in `/plan`, `/review` and `/design` working.

For everyday work, just type your request. The rules always apply, and these skills can activate on their own when relevant: `karpathy-guidelines` (coding), `pros-graph` (large repo exploration), `hallmark` (new web pages), `mobile-design` (React Native), `mcp-builder` and `skill-creator`. Only short descriptions load until a skill is used. Tests and reviews never start by themselves.

### Spec Kit commands

These need the Spec Kit step from [section 3](#3-commands-to-run-per-repo). Run them one at a time and review each result.

| Command | What it does | Example |
|---|---|---|
| `/speckit-constitution` | Sets project-wide principles. Run once per project. | `/speckit-constitution Focus on fast pages, accessibility and simple code` |
| `/speckit-specify` | Describes what to build and why. | `/speckit-specify A home page with a hero, features and a sign-up button` |
| `/speckit-clarify` | Optional. Asks up to 5 questions that fill gaps in the spec. | `/speckit-clarify` |
| `/speckit-plan` | Chooses how to build it. | `/speckit-plan Use Next.js and our existing components` |
| `/speckit-checklist` | Optional. Creates a quality checklist for the requirements. | `/speckit-checklist` |
| `/speckit-tasks` | Breaks the plan into ordered tasks. | `/speckit-tasks` |
| `/speckit-analyze` | Optional. Checks that the spec, plan and tasks agree. | `/speckit-analyze` |
| `/speckit-implement` | Builds the code from the tasks. | `/speckit-implement` |
| `/speckit-converge` | Compares the code with the spec and adds tasks for anything unbuilt. | `/speckit-converge` |

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
