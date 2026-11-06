"""Health checks. Runs nothing that launches a browser, emulator or test suite."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from . import agents as ag
from .core import Manifest, load_lock, state_dir

COMMANDS = ("pros-plan", "pros-implement", "pros-review", "pros-audit", "pros-design", "pros-graph",
            "pros-test-web", "pros-test-mobile", "pros-test-components", "pros-tokens")


class Report:
    def __init__(self) -> None:
        self.failed = 0

    def __call__(self, level: str, message: str) -> None:
        self.failed += level == "fail"
        print(f"[{level}] {message}")


def version(command: list) -> str:
    try:
        run = subprocess.run(command, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    lines = (run.stdout or run.stderr).strip().splitlines()
    return lines[-1][:60] if run.returncode == 0 and lines else ""


def check_agents(report: Report, manifest: Manifest) -> None:
    print("\nAgents")
    for agent in ag.all_agents():
        managed = agent.id in manifest.agents
        if not agent.detected and not managed:
            report("info", f"{agent.name}: not detected")
            continue
        report("ok" if managed else "warn",
               f"{agent.name}: {'installed' if managed else 'detected, not installed'}; tests {agent.enforcement}")
        if not managed:
            continue
        for directory in agent.skills_dirs:
            missing = [name for name in COMMANDS if not (directory / name / "SKILL.md").exists()]
            report("fail" if missing else "ok",
                   f"  {directory}: " + (f"missing {', '.join(missing)}" if missing else "all 10 commands present"))
        for path in (agent.rules_block, agent.rules_file, agent.codex_rules, agent.ask_settings):
            if path:
                report("ok" if path.exists() else "fail", f"  {path}")


def check_skills(report: Report) -> None:
    print("\nSkills")
    root = state_dir() / "skills"
    names = sorted(p.name for p in root.iterdir()) if root.exists() else []
    report("ok" if names else "fail", f"{len(names)} skills: {', '.join(names)}")
    for item in load_lock()["upstream"]:
        stamp = state_dir() / "upstream" / f"{item['id']}.verified"
        good = stamp.exists() and stamp.read_text().strip() == item["tree_sha256"]
        report("ok" if good else "warn", f"{item['id']}: {'verified at ' + item['commit'][:7] if good else 'not installed'}")


def check_tools(report: Report) -> None:
    print("\nTools")
    lock = load_lock()
    for name, command, pin in (("graphify", ["graphify", "--version"], lock["pypi"]["graphifyy"]),
                               ("specify", ["specify", "--version"], lock["pypi"]["specify-cli"])):
        found = version(command) if shutil.which(name) else ""
        report("ok" if found else "warn", f"{name}: {found or 'not installed'} (pin {pin})")
    maestro = shutil.which("maestro") or state_dir() / "bin" / "maestro"
    found = version([str(maestro), "--version"]) if Path(str(maestro)).exists() else ""
    report("ok" if found else "info", f"maestro: {found or 'not installed (pros install --with-maestro)'}")
    report("ok" if shutil.which("java") else "info", f"java for maestro: {'found' if shutil.which('java') else 'missing'}")
    run = subprocess.run(["npm", "ls", "-g", "--depth=0", "puppeteer-core"], capture_output=True, text=True) \
        if shutil.which("npm") else None
    if run and "puppeteer-core" in run.stdout:
        report("warn", "puppeteer-core is global: Hallmark can open a browser during builds")
    print("\nThis project (not run, only detected)")
    package = Path("package.json")
    deps = {}
    if package.exists():
        data = json.loads(package.read_text(encoding="utf-8"))
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
    report("info", f"Playwright: {'found' if '@playwright/test' in deps else 'not in package.json'}")
    report("info", f"RN Testing Library: {'found' if '@testing-library/react-native' in deps else 'not in package.json'}")
    report("info", f"Maestro flows: {'found' if Path('.maestro').is_dir() else 'no .maestro folder'}")


def check_tokens(report: Report) -> None:
    print("\nToken reporting")
    script = state_dir() / "upstream" / "token-usage" / "scripts" / "token_usage.py"
    good = script.exists() and version([sys.executable, "-I", str(script), "report", "--help"])
    report("ok" if good else "fail", f"token-usage: {'runs locally' if good else 'not working'}")
    pin = load_lock()["npm"]["ccusage"]
    found = version(["npx", "--yes", f"ccusage@{pin}", "--version"]) if shutil.which("npx") else ""
    report("ok" if found else "warn", f"ccusage: {found or 'npx could not run it'} (pin {pin})")


def check_mcp(report: Report) -> None:
    print("\nMCP")
    found = shutil.which("graphify-mcp")
    report("info", f"graphify-mcp: {'available' if found else 'not installed'}. The toolkit configures no MCP servers.")


def doctor(_args) -> int:
    report = Report()
    manifest = Manifest()
    print(f"Toolkit: {state_dir()} ({'installed' if manifest.path.exists() else 'not installed'})")
    report("ok" if shutil.which("pros") else "warn",
           "pros on PATH" if shutil.which("pros") else f"pros not on PATH, use {state_dir() / 'bin' / 'pros'}")
    check_agents(report, manifest)
    check_skills(report)
    check_tools(report)
    check_tokens(report)
    check_mcp(report)
    print(f"\n{report.failed} failed checks." if report.failed else "\nAll required checks passed.")
    return 1 if report.failed else 0
