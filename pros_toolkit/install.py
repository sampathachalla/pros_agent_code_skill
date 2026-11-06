"""Install, update and uninstall."""
from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

from . import agents as ag
from .core import (REPO, Change, Manifest, apply_change, ensure_dir, load_lock, merge_ask, read, revert_file,
                   sha256, state_dir, upsert_block)
from .upstream import sync_item

MARKER = ".pros-toolkit"  # marks a copied skill on systems without symlinks
OPENAI_YAML = "policy:\n  allow_implicit_invocation: false\n"
APP_ITEMS = ("pros.py", "pros_toolkit", "skills", "rules", "adapters", "toolkit.lock.json")


def rules_text() -> str:
    names = ("global", "coding", "security", "testing", "token-efficiency")
    parts = [(REPO / "rules" / f"{name}.md").read_text(encoding="utf-8").strip() for name in names]
    return "\n\n".join(parts) + "\n"


def antigravity_rule() -> bytes:
    head = '---\ntrigger: always_on\ndescription: "Pros Toolkit coding, security, testing and token rules."\n---\n\n'
    return (head + rules_text()).encode("utf-8")


def plan_changes(selected: List[ag.Agent], manifest: Manifest) -> List[Change]:
    changes: List[Change] = []
    for agent in selected:
        if agent.rules_block:
            text = (read(agent.rules_block) or b"").decode("utf-8")
            new = upsert_block(text, rules_text()).encode("utf-8")
            changes.append(Change(agent.rules_block, new, "block"))
        if agent.rules_file:
            changes.append(Change(agent.rules_file, antigravity_rule(), "own"))
        if agent.codex_rules:
            changes.append(Change(agent.codex_rules, ag.codex_rules_text().encode("utf-8"), "own"))
        if agent.ask_settings:
            rules = ag.claude_rules() if agent.id == "claude" else ag.antigravity_rules()
            previous = manifest.files.get(str(agent.ask_settings), {}).get("owned", [])
            new, owned = merge_ask(read(agent.ask_settings) or b"", rules, previous)
            changes.append(Change(agent.ask_settings, new, "json-ask", owned))
    return changes


def is_manual(skill_dir: Path) -> bool:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    return re.search(r"^disable-model-invocation:\s*true\s*$", text, re.M) is not None


def build_skills(items: List[dict]) -> List[str]:
    """Regenerate ~/.pros-toolkit/skills from local and verified upstream skills."""
    root = state_dir() / "skills"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    names = []
    for source in sorted(p for p in (REPO / "skills").iterdir() if (p / "SKILL.md").exists()):
        target = root / source.name
        shutil.copytree(str(source), str(target))
        if is_manual(target):
            (target / "agents").mkdir(exist_ok=True)
            (target / "agents" / "openai.yaml").write_text(OPENAI_YAML, encoding="utf-8")
        names.append(source.name)
    for item in items:
        if item["install"] == "skill":
            shutil.copytree(str(state_dir() / "upstream" / item["id"]), str(root / item["id"]))
            names.append(item["id"])
    return names


def is_ours(link: Path) -> bool:
    if link.is_symlink():
        return str(state_dir()) in os.readlink(str(link))
    return (link / MARKER).exists()


def remove_link(link: Path) -> None:
    if link.is_symlink():
        link.unlink()
    elif link.is_dir():
        shutil.rmtree(link)


def link_skills(names: List[str], dirs: List[Path], manifest: Manifest) -> List[str]:
    conflicts, wanted = [], set()
    for directory in dirs:
        ensure_dir(directory, manifest)
        for name in names:
            link, target = directory / name, state_dir() / "skills" / name
            exists = link.exists() or link.is_symlink()
            if exists and not is_ours(link):
                conflicts.append(str(link))
                continue
            if exists:
                remove_link(link)
            try:
                link.symlink_to(target, target_is_directory=True)
            except OSError:  # Windows without developer mode
                shutil.copytree(str(target), str(link))
                (link / MARKER).write_text("managed by pros-toolkit\n", encoding="utf-8")
            wanted.add(str(link))
    for stale in set(manifest.links) - wanted:
        if is_ours(Path(stale)):
            remove_link(Path(stale))
    manifest.links = sorted(wanted)
    return conflicts


def install_app(manifest: Manifest) -> Optional[str]:
    """Copy the CLI so it survives deleting the clone, and put it on PATH."""
    app = state_dir() / "app"
    if app.exists():
        shutil.rmtree(app)
    app.mkdir(parents=True)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    for item in APP_ITEMS:
        source = REPO / item
        if source.is_dir():
            shutil.copytree(str(source), str(app / item), ignore=ignore)
        else:
            shutil.copy2(str(source), str(app / item))
    bin_dir = state_dir() / "bin"
    bin_dir.mkdir(exist_ok=True)
    launcher = bin_dir / "pros"
    launcher.write_text(f'#!/bin/sh\nexec python3 "{app / "pros.py"}" "$@"\n', encoding="utf-8")
    launcher.chmod(launcher.stat().st_mode | stat.S_IEXEC)
    (bin_dir / "pros.cmd").write_text(f'@py -3 "{app / "pros.py"}" %*\r\n', encoding="utf-8")
    if sys.platform == "win32":
        return f"Add {bin_dir} to PATH to use `pros`."
    local_bin = Path.home() / ".local" / "bin"
    ensure_dir(local_bin, manifest)
    link = local_bin / "pros"
    if link.exists() or link.is_symlink():
        if not is_ours(link):
            return f"{link} exists and is not ours; use {launcher} instead."
        link.unlink()
    link.symlink_to(launcher)
    if str(local_bin) not in os.environ.get("PATH", "").split(os.pathsep):
        return f"Add {local_bin} to PATH to use `pros`."
    return None


def install_pypi(pins: Dict[str, str], manifest: Manifest) -> List[str]:
    if not shutil.which("uv"):
        return [f"uv not found, skipped {', '.join(pins)}. See https://docs.astral.sh/uv/"]
    listed = subprocess.run(["uv", "tool", "list"], capture_output=True, text=True).stdout
    messages = []
    for package, version in pins.items():
        current = re.search(rf"^{re.escape(package)} v(\S+)", listed, re.M)
        if current and current.group(1) == version:
            continue
        if current and package not in manifest.tools:
            messages.append(f"{package} {current.group(1)} is yours, left in place (pin is {version}).")
            continue
        result = subprocess.run(["uv", "tool", "install", "--force", f"{package}=={version}"],
                                capture_output=True, text=True)
        if result.returncode != 0:
            messages.append(f"{package}: uv failed: {result.stderr.strip()[-300:]}")
        elif package not in manifest.tools:
            manifest.tools.append(package)
    return messages


def install_maestro(pin: dict, manifest: Manifest) -> List[str]:
    if shutil.which("maestro") and "maestro" not in manifest.tools:
        return ["maestro already on PATH, left in place."]
    root = state_dir() / "tools"
    stamp = root / "maestro.version"
    if stamp.exists() and stamp.read_text().strip() == pin["version"]:
        return []
    root.mkdir(parents=True, exist_ok=True)
    archive = root / "maestro.zip"
    try:
        urllib.request.urlretrieve(pin["url"], str(archive))
    except OSError as error:
        archive.unlink(missing_ok=True)
        return [f"maestro: download failed ({error}). Rerun `pros install --with-maestro`."]
    if sha256(archive.read_bytes()) != pin["sha256"]:
        archive.unlink()
        return ["maestro: checksum mismatch, nothing installed."]
    target = root / "maestro"
    if target.exists():
        shutil.rmtree(target)
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            if not (root / member.filename).resolve().is_relative_to(root.resolve()):
                archive.unlink()
                return ["maestro: unsafe path in archive, nothing installed."]
        bundle.extractall(str(root))
    archive.unlink()
    binary = target / "bin" / "maestro"
    binary.chmod(binary.stat().st_mode | stat.S_IEXEC)
    stamp.write_text(pin["version"] + "\n", encoding="utf-8")
    if sys.platform != "win32":
        wrapper = state_dir() / "bin" / "maestro"
        wrapper.write_text(f'#!/bin/sh\nMAESTRO_CLI_NO_ANALYTICS=1 exec "{binary}" "$@"\n', encoding="utf-8")
        wrapper.chmod(wrapper.stat().st_mode | stat.S_IEXEC)
        link = Path.home() / ".local" / "bin" / "maestro"
        if link.is_symlink():
            link.unlink()
        link.symlink_to(wrapper)
    if "maestro" not in manifest.tools:
        manifest.tools.append("maestro")
    return []


def select_agents(names: Optional[str]) -> List[ag.Agent]:
    agents = ag.all_agents()
    if names:
        wanted = [name.strip() for name in names.split(",")]
        unknown = set(wanted) - set(ag.SUPPORTED)
        if unknown:
            raise SystemExit(f"Unknown agents: {', '.join(sorted(unknown))}. Choose from {', '.join(ag.SUPPORTED)}.")
        return [agent for agent in agents if agent.id in wanted]
    return [agent for agent in agents if agent.detected]


def confirm(args, changes: List[Change]) -> bool:
    if args.yes:
        return True
    if not sys.stdin.isatty():
        print("\nNot a terminal, nothing changed. Review with --dry-run, then rerun with --yes.")
        return False
    return input("\nApply these changes? [y/N] ").strip().lower() in ("y", "yes")


def install(args) -> int:
    lock = load_lock()
    manifest = Manifest()
    selected = select_agents(args.agents)
    if not selected:
        print("No supported agents found. Use --agents to choose some.")
        return 1
    print("Agents: " + ", ".join(agent.name for agent in selected))
    try:
        changes = plan_changes(selected, manifest)
    except (ValueError, UnicodeDecodeError) as error:
        print(f"Stopped before changing anything: {error}. Fix that config file and rerun.")
        return 1
    dirs: List[Path] = []
    for agent in selected:
        dirs += [d for d in agent.skills_dirs if d not in dirs]
    print("Skill folders:\n  " + "\n  ".join(str(d) for d in dirs))
    pending = [change for change in changes if not change.is_noop]
    print(f"\nConfig changes: {len(pending)}")
    for change in pending:
        print(change.diff() or f"new file {change.path}")
    if args.dry_run:
        print("\nDry run: nothing changed.")
        return 0
    if not confirm(args, pending):
        return 1

    items = [] if args.skip_upstream else lock["upstream"]
    try:
        for item in items:
            print(f"Verifying {item['id']}")
            sync_item(item)
    except (ValueError, subprocess.CalledProcessError) as error:
        print(f"Stopped before changing agent config: {error}")
        return 1

    # Save after every step: an interrupted install must stay reversible.
    manifest.source_repo = str(REPO) if (REPO / ".git").exists() else manifest.source_repo
    manifest.agents = sorted(set(manifest.agents) | {agent.id for agent in selected})
    manifest.save()
    messages = [install_app(manifest)]
    manifest.save()
    names = build_skills(items)
    conflicts = link_skills(names, dirs, manifest)
    manifest.save()
    for change in changes:
        if not change.is_noop:
            apply_change(change, manifest)
            manifest.save()
    if not args.skip_tools:
        messages += install_pypi(lock["pypi"], manifest)
        manifest.save()
        if args.with_maestro:
            messages += install_maestro(lock["maestro"], manifest)
            manifest.save()

    print(f"\nInstalled {len(names)} skills for {len(selected)} agents.")
    for path in conflicts:
        print(f"[warn] kept your existing {path}; that skill was not linked there.")
    for message in filter(None, messages):
        print(f"[warn] {message}")
    for agent in selected:
        for note in agent.notes:
            print(f"[note] {agent.name}: {note}")
    print("Check it with: pros doctor")
    return 0


def update(args) -> int:
    source = Manifest().source_repo
    if not source or not Path(source, ".git").exists():
        print("Clone not found. Clone the repo again and run scripts/install.sh.")
        return 1
    result = subprocess.run(["git", "-C", source, "pull", "--ff-only"])
    if result.returncode != 0:
        print("git pull failed, nothing changed.")
        return 1
    command = [sys.executable, str(Path(source) / "pros.py"), "install"]
    command += ["--yes"] * args.yes + ["--dry-run"] * args.dry_run
    command += ["--with-maestro"] * ("maestro" in Manifest().tools)
    return subprocess.run(command).returncode


def uninstall(args) -> int:
    manifest = Manifest()
    if not manifest.path.exists():
        print("Nothing to uninstall: no manifest found.")
        return 1
    print("Will remove:")
    for path in manifest.links + list(manifest.files) + manifest.tools + [str(state_dir())]:
        print(f"  {path}")
    if args.dry_run:
        print("\nDry run: nothing changed.")
        return 0
    if not confirm(args, []):
        return 1
    for link in manifest.links:
        if is_ours(Path(link)):
            remove_link(Path(link))
    for key, record in manifest.files.items():
        print(revert_file(key, record))
    for tool in manifest.tools:
        if tool == "maestro":
            continue
        subprocess.run(["uv", "tool", "uninstall", tool], capture_output=True)
    local_bin = Path.home() / ".local" / "bin"
    for name in ("pros", "maestro"):
        link = local_bin / name
        if link.is_symlink() and is_ours(link):
            link.unlink()
    shutil.rmtree(state_dir())
    for directory in sorted(manifest.dirs, key=len, reverse=True):
        try:
            Path(directory).rmdir()
        except OSError:
            pass
    print("Uninstalled.")
    return 0
