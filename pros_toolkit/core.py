"""Paths, the install manifest and reversible file edits."""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

REPO = Path(__file__).resolve().parent.parent
BLOCK_START = "<!-- pros-toolkit:start -->"
BLOCK_END = "<!-- pros-toolkit:end -->"


def state_dir() -> Path:
    return Path.home() / ".pros-toolkit"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read(path: Path) -> Optional[bytes]:
    return path.read_bytes() if path.is_file() else None


def load_lock() -> dict:
    return json.loads((REPO / "toolkit.lock.json").read_text(encoding="utf-8"))


class Manifest:
    """Records everything the toolkit changed, so uninstall can reverse it."""

    def __init__(self) -> None:
        self.path = state_dir() / "manifest.json"
        data = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}
        self.source_repo = data.get("source_repo", "")
        self.agents: List[str] = data.get("agents", [])
        self.files: dict = data.get("files", {})
        self.links: List[str] = data.get("links", [])
        self.dirs: List[str] = data.get("dirs", [])
        self.tools: List[str] = data.get("tools", [])

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "source_repo": self.source_repo,
            "agents": self.agents,
            "files": self.files,
            "links": self.links,
            "dirs": self.dirs,
            "tools": self.tools,
        }
        self.path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def ensure_dir(path: Path, manifest: Manifest) -> None:
    """mkdir -p that remembers which directories it created."""
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    for directory in reversed(missing):
        directory.mkdir()
        manifest.dirs.append(str(directory))


def write_atomic(path: Path, data: bytes) -> None:
    target = Path(os.path.realpath(path))
    fd, tmp = tempfile.mkstemp(dir=str(target.parent), prefix=".pros-")
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)
    if target.exists():
        shutil.copymode(str(target), tmp)
    else:
        os.chmod(tmp, 0o644)
    os.replace(tmp, str(target))


def upsert_block(text: str, body: str) -> str:
    """Insert or replace the managed block, leaving other text untouched."""
    start, end = text.find(BLOCK_START), text.find(BLOCK_END)
    if (start == -1) != (end == -1) or end < start:
        raise ValueError("unbalanced pros-toolkit markers")
    block = f"{BLOCK_START}\n{body.rstrip()}\n{BLOCK_END}"
    if start != -1:
        return text[:start] + block + text[end + len(BLOCK_END):]
    if text and not text.endswith("\n"):
        text += "\n"
    return f"{text}\n{block}\n" if text else f"{block}\n"


def strip_block(text: str) -> str:
    start, end = text.find(BLOCK_START), text.find(BLOCK_END)
    if start == -1 or end < start:
        return text
    before, after = text[:start], text[end + len(BLOCK_END):]
    if after.startswith("\n"):
        after = after[1:]
    if before.endswith("\n\n"):
        before = before[:-1]
    return before + after


def merge_ask(data: bytes, rules: List[str], previous: List[str]) -> tuple:
    """Add ask rules to a JSON settings file; returns (new bytes, rules we own)."""
    settings = json.loads(data.decode("utf-8")) if data and data.strip() else {}
    ask = settings.setdefault("permissions", {}).setdefault("ask", [])
    ask[:] = [rule for rule in ask if rule not in previous or rule in rules]
    owned = [rule for rule in rules if rule in previous or rule not in ask]
    ask.extend(rule for rule in owned if rule not in ask)
    return (json.dumps(settings, indent=2) + "\n").encode("utf-8"), owned


def remove_ask(data: bytes, rules: List[str]) -> bytes:
    settings = json.loads(data.decode("utf-8"))
    permissions = settings.get("permissions", {})
    ask = [rule for rule in permissions.get("ask", []) if rule not in rules]
    if ask:
        permissions["ask"] = ask
    else:
        permissions.pop("ask", None)
    if not permissions:
        settings.pop("permissions", None)
    return (json.dumps(settings, indent=2) + "\n").encode("utf-8")


@dataclass
class Change:
    """A pending edit to a file outside the toolkit's own directory."""

    path: Path
    new: bytes
    kind: str  # block | json-ask | own
    owned: List[str] = field(default_factory=list)

    @property
    def old(self) -> Optional[bytes]:
        return read(self.path)

    @property
    def is_noop(self) -> bool:
        return self.old == self.new

    def diff(self) -> str:
        old = (self.old or b"").decode("utf-8", "replace").splitlines()
        new = self.new.decode("utf-8", "replace").splitlines()
        lines = difflib.unified_diff(old, new, str(self.path), str(self.path), lineterm="", n=1)
        return "\n".join(lines)


def apply_change(change: Change, manifest: Manifest) -> None:
    key = str(change.path)
    record = manifest.files.get(key)
    if record is None:
        old = change.old
        record = {"action": "created" if old is None else "modified", "kind": change.kind}
        if old is not None:
            backups = state_dir() / "backups"
            backups.mkdir(parents=True, exist_ok=True)
            backup = backups / f"{sha256(key.encode())[:12]}-{change.path.name}"
            backup.write_bytes(old)
            record["backup"] = str(backup)
    ensure_dir(change.path.parent, manifest)
    write_atomic(change.path, change.new)
    record["post_sha"] = sha256(change.new)
    record["owned"] = change.owned
    manifest.files[key] = record


def revert_file(key: str, record: dict) -> str:
    """Undo one tracked edit. Restores exact bytes unless the user edited it since."""
    path = Path(key)
    current = read(path)
    if current is None:
        return f"already gone: {key}"
    untouched = sha256(current) == record.get("post_sha")
    if untouched:
        if record["action"] == "created":
            path.unlink()
            return f"removed {key}"
        write_atomic(path, Path(record["backup"]).read_bytes())
        return f"restored {key}"
    if record["kind"] == "own":
        return f"kept {key}: edited since install, delete it yourself if unwanted"
    if record["kind"] == "block":
        new = strip_block(current.decode("utf-8")).encode("utf-8")
    else:
        new = remove_ask(current, record.get("owned", []))
    write_atomic(path, new)
    return f"removed toolkit entries from {key}, kept your later edits"
