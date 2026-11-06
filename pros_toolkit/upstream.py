"""Fetch pinned upstream files and verify them against the lock file."""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

from .core import state_dir


def tree_hash(root: Path) -> str:
    """Hash file paths and contents, so results don't depend on archive format."""
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() or p.is_symlink()):
        if path.is_symlink():
            raise ValueError(f"symlink in upstream content: {path}")
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *args], cwd=str(cwd), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def fetch(item: dict, dest: Path) -> str:
    """Check out the pinned paths into dest and return their tree hash."""
    with tempfile.TemporaryDirectory(prefix="pros-fetch-") as tmp:
        work = Path(tmp)
        _git(work, "init", "-q")
        _git(work, "remote", "add", "origin", item["repo"])
        _git(work, "sparse-checkout", "set", "--no-cone", *[f"/{p}" for p in item["paths"]])
        _git(work, "fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", item["commit"])
        _git(work, "checkout", "-q", "FETCH_HEAD")
        source = work / item.get("strip", "")
        shutil.rmtree(work / ".git")
        result = tree_hash(source)
        if dest.exists():
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(str(source), str(dest))
    return result


def sync_item(item: dict) -> Path:
    """Fetch one item unless the verified copy is already in place."""
    dest = state_dir() / "upstream" / item["id"]
    stamp = dest.parent / f"{item['id']}.verified"
    expected = item["tree_sha256"]
    if dest.exists() and stamp.exists() and stamp.read_text().strip() == expected:
        return dest
    actual = fetch(item, dest)
    if actual != expected:
        shutil.rmtree(dest)
        raise ValueError(f"{item['id']}: hash mismatch, expected {expected}, got {actual}")
    stamp.write_text(expected + "\n", encoding="utf-8")
    return dest
