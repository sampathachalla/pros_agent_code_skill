"""Optional per-repo setup. Global skills work without it."""
from __future__ import annotations

from pathlib import Path

from .install import rules_text

HEADER = "---\ndescription: Pros Toolkit coding, security, testing and token rules\nalwaysApply: true\n---\n\n"


def init(args) -> int:
    rule = Path(args.path).resolve() / ".cursor" / "rules" / "pros-toolkit.mdc"
    if args.remove:
        if not rule.exists():
            print(f"Nothing to remove at {rule}.")
            return 0
        if args.dry_run:
            print(f"Would remove {rule}")
            return 0
        rule.unlink()
        print(f"Removed {rule}")
        return 0
    content = HEADER + rules_text()
    if rule.exists() and rule.read_text(encoding="utf-8") == content:
        print("Already up to date.")
        return 0
    if args.dry_run:
        print(f"Would write {rule}")
        return 0
    rule.parent.mkdir(parents=True, exist_ok=True)
    rule.write_text(content, encoding="utf-8")
    print(f"Wrote {rule}\nCommit it so everyone using Cursor on this repo gets the rules.")
    return 0
