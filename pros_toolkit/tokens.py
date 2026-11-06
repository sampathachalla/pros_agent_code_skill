"""Local token reports. Makes no LLM calls and sends no session data anywhere."""
from __future__ import annotations

import datetime
import re
import shutil
import subprocess
import sys

from .core import load_lock, state_dir

# toolkit name -> (token-usage runtime, ccusage source or None)
RUNTIMES = {
    "claude": ("claude", "claude"),
    "codex": ("codex", "codex"),
    "cursor": ("cursor", None),
    "antigravity": ("gemini", "antigravity"),
}


def since_date(since: str) -> str:
    match = re.fullmatch(r"(\d+)d", since)
    if not match:
        raise SystemExit("--since must look like 7d")
    day = datetime.date.today() - datetime.timedelta(days=int(match.group(1)))
    return day.strftime("%Y%m%d")


def run_token_usage(*args: str) -> int:
    script = state_dir() / "upstream" / "token-usage" / "scripts" / "token_usage.py"
    if not script.exists():
        print("token-usage is not installed. Run `pros install`.")
        return 1
    return subprocess.run([sys.executable, "-I", str(script), *args]).returncode


def tokens(args) -> int:
    runtime, source = RUNTIMES[args.agent]
    print("All figures are read from local session logs. Token counts are what the agent recorded;\n"
          "costs are API-price estimates, not your subscription bill.\n")
    print(f"## Latest session, by activity and skill ({args.agent}, token-usage)\n")
    code = run_token_usage("report", "--runtime", runtime)
    if args.session:
        return code
    print(f"\n## Expensive activities, last {args.since} (token-usage)\n")
    run_token_usage("history", "--by", "command", "--since", args.since, "--runtime", runtime)
    print(f"\n## Findings, last {args.since} (token-usage, arithmetic only)\n")
    run_token_usage("insights", "--since", args.since, "--runtime", runtime)
    if source is None:
        print("\nccusage has no Cursor report; token-usage above is the only source.")
    elif shutil.which("npx"):
        print(f"\n## Daily totals, last {args.since} (ccusage, offline pricing)\n")
        pin = load_lock()["npm"]["ccusage"]
        subprocess.run(["npx", "--yes", f"ccusage@{pin}", source, "daily", "--offline",
                        "--since", since_date(args.since)])
    return code
