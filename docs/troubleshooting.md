# Troubleshooting

Start with `pros doctor`. It doesn't run tests or open a browser.

| Problem | Fix |
|---|---|
| `pros: command not found` | Add `~/.local/bin` to `PATH`, or use `~/.pros-toolkit/bin/pros`. |
| A command doesn't appear in an agent | Start a new session. In `agy`, run `/skills reload`. Then run `pros doctor`. |
| `kept your existing ...` | A skill with that name already exists. Rename or remove yours, then run `pros install`. |
| `Not a terminal, nothing changed` | Review with `--dry-run`, then rerun with `--yes`. |
| `Stopped before changing anything` | A config file is malformed or has broken markers. Fix it and rerun. |
| `hash mismatch` | Upstream content didn't match the lock file, so nothing was changed. Don't work around this: check the pin first. |
| `uv not found` | Install [uv](https://docs.astral.sh/uv/), then run `pros install`. |
| `... is yours, left in place` | You already had that tool at another version. The toolkit won't change it. |
| Graphify answers are large | Ask narrower questions, or use `--budget`. |
| `pros tokens` shows nothing | That agent has no local sessions yet, or try `--agent`. |
| Every `npm test` prompts | Expected: tests need approval. Remove that rule from your agent's config to change it. |
| Hallmark says `render tier not run` | Expected: browser checks are off unless you install `puppeteer-core`. |
