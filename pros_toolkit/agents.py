"""Where each supported agent keeps its global skills, rules and permissions."""
from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .core import REPO

SUPPORTED = ("claude", "codex", "cursor", "antigravity")


def claude_home() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def _app(name: str) -> bool:
    return sys.platform == "darwin" and Path("/Applications", name).exists()


@dataclass
class Agent:
    id: str
    name: str
    evidence: List[str]
    skills_dirs: List[Path]
    enforcement: str
    rules_block: Optional[Path] = None
    rules_file: Optional[Path] = None
    ask_settings: Optional[Path] = None
    codex_rules: Optional[Path] = None
    notes: List[str] = field(default_factory=list)

    @property
    def detected(self) -> bool:
        return bool(self.evidence)


def _evidence(bins: List[str], paths: List[Path], apps: List[str]) -> List[str]:
    found = [f"{name} on PATH" for name in bins if shutil.which(name)]
    found += [str(path) for path in paths if path.exists()]
    found += [f"/Applications/{app}" for app in apps if _app(app)]
    return found


def all_agents() -> List[Agent]:
    home = Path.home()
    gemini = home / ".gemini"
    agy_dir = gemini / "antigravity-cli"
    has_agy = bool(shutil.which("agy")) or agy_dir.exists()
    agents_skills = home / ".agents" / "skills"
    return [
        Agent(
            "claude", "Claude Code",
            _evidence(["claude"], [claude_home()], []),
            [claude_home() / "skills"],
            "enforced: permissions.ask rules",
            rules_block=claude_home() / "CLAUDE.md",
            ask_settings=claude_home() / "settings.json",
        ),
        Agent(
            "codex", "Codex",
            _evidence(["codex"], [codex_home()], []),
            [agents_skills],
            "enforced: execpolicy prompt rules",
            rules_block=codex_home() / "AGENTS.md",
            codex_rules=codex_home() / "rules" / "pros-toolkit.rules",
        ),
        Agent(
            "cursor", "Cursor",
            _evidence(["cursor", "cursor-agent"], [home / ".cursor"], ["Cursor.app"]),
            [agents_skills],
            "instructions only: no documented global permission file",
            notes=["Global rules live in Cursor Settings; run `pros init` in a repo for always-on rules."],
        ),
        Agent(
            "antigravity", "Antigravity",
            _evidence(
                ["agy"],
                [gemini / "antigravity", gemini / "antigravity-ide", agy_dir, gemini / "config"],
                ["Antigravity.app", "Antigravity IDE.app"],
            ),
            [gemini / "config" / "skills"],
            "enforced in agy; instructions only in the app and IDE" if has_agy
            else "instructions only: install agy for enforced ask rules",
            rules_file=gemini / "config" / "rules" / "pros-toolkit.md",
            ask_settings=agy_dir / "settings.json" if has_agy else None,
        ),
    ]


def test_commands() -> List[str]:
    path = REPO / "adapters" / "test-commands.json"
    return json.loads(path.read_text(encoding="utf-8"))


def claude_rules() -> List[str]:
    rules = []
    for command in test_commands():
        rules.append(f"Bash({command})" if command.endswith("*") else f"Bash({command} *)")
    return rules


def antigravity_rules() -> List[str]:
    return [f"command({command.rstrip('*')})" for command in test_commands()]


def codex_rules_text() -> str:
    lines = ["# Managed by pros-toolkit. Tests and emulators run only after you approve them."]
    for command in test_commands():
        pattern = json.dumps(command.rstrip("*").split())
        lines.append(
            f'prefix_rule(pattern={pattern}, decision="prompt", '
            'justification="pros-toolkit: run tests only on explicit request")'
        )
    return "\n".join(lines) + "\n"
