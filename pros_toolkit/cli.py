"""Command-line interface."""
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile
from typing import List, Optional

from . import __version__
from .doctor import doctor
from .install import install, uninstall, update
from .project import init
from .tokens import RUNTIMES, tokens
from .core import load_lock
from .upstream import fetch


def verify_pins(_args) -> int:
    """Maintainer helper: fetch every pin and compare it with the lock file."""
    bad = 0
    for item in load_lock()["upstream"]:
        with tempfile.TemporaryDirectory(prefix="pros-pin-") as tmp:
            actual = fetch(item, Path(tmp) / "item")
        same = actual == item["tree_sha256"]
        bad += not same
        print(f"[{'ok' if same else 'diff'}] {item['id']} {actual}")
    return 1 if bad else 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="pros", description="Shared skills and rules for coding agents.")
    root.add_argument("--version", action="version", version=__version__)
    commands = root.add_subparsers(dest="command", required=True)

    def add(name: str, handler, help_text: str, changes: bool = True) -> argparse.ArgumentParser:
        command = commands.add_parser(name, help=help_text)
        command.set_defaults(handler=handler)
        if changes:
            command.add_argument("--dry-run", action="store_true", help="show changes and exit")
        return command

    def add_yes(command: argparse.ArgumentParser) -> None:
        command.add_argument("--yes", action="store_true", help="apply without asking")

    run = add("install", install, "install globally")
    add_yes(run)
    run.add_argument("--agents", help="comma list: claude,codex,cursor,antigravity (default: detected)")
    run.add_argument("--with-maestro", action="store_true", help="also install the pinned Maestro CLI")
    run.add_argument("--skip-tools", action="store_true", help="skip graphify, specify and maestro")
    run.add_argument("--skip-upstream", action="store_true", help="skip pinned upstream skills")
    add_yes(add("update", update, "git pull, then reinstall"))
    add_yes(add("uninstall", uninstall, "reverse the install"))
    add("doctor", doctor, "check the installation", changes=False)
    add("verify-pins", verify_pins, "maintainers: check lock hashes", changes=False)

    repo = add("init", init, "add Cursor always-on rules to a repo")
    repo.add_argument("path", nargs="?", default=".")
    repo.add_argument("--remove", action="store_true")

    usage = add("tokens", tokens, "local token report", changes=False)
    usage.add_argument("--agent", choices=sorted(RUNTIMES), default="claude")
    usage.add_argument("--since", default="7d", help="period such as 7d")
    usage.add_argument("--session", action="store_true", help="latest session only")
    return root


def main(argv: Optional[List[str]] = None) -> int:
    args = parser().parse_args(argv)
    return args.handler(args)
