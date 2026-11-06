"""Isolated tests. Every run uses a throwaway HOME and never touches real configs."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pros_toolkit import agents, core  # noqa: E402

ALL = "claude,codex,cursor,antigravity"
USER_CLAUDE = "# My rules\n\nKeep this exactly.\n"
USER_SETTINGS = '{\n    "theme": "dark",\n    "permissions": {"allow": ["Bash(ls)"], "ask": ["Bash(rm *)"]}\n}\n'
USER_DEFAULT_RULES = 'prefix_rule(pattern=["npm", "test"], decision="allow")\n'


def snapshot(root):
    return {
        str(p.relative_to(root)): (p.read_bytes() if p.is_file() and not p.is_symlink() else "dir")
        for p in sorted(root.rglob("*"))
    }


class Block(unittest.TestCase):
    def test_round_trip_keeps_text(self):
        for text in ("", "a\n", "a", "a\n\nb\n"):
            added = core.upsert_block(text, "rules")
            self.assertEqual(core.upsert_block(added, "rules"), added)
            self.assertEqual(core.strip_block(added), text if text != "a" else "a\n")

    def test_unbalanced_markers_rejected(self):
        with self.assertRaises(ValueError):
            core.upsert_block(core.BLOCK_START, "rules")


class Ask(unittest.TestCase):
    def test_never_claims_user_rules(self):
        data = json.dumps({"permissions": {"ask": ["Bash(jest *)"]}}).encode()
        new, owned = core.merge_ask(data, ["Bash(jest *)", "Bash(pytest *)"], [])
        self.assertEqual(owned, ["Bash(pytest *)"])
        self.assertEqual(json.loads(core.remove_ask(new, owned))["permissions"]["ask"], ["Bash(jest *)"])

    def test_dropped_rules_are_removed_on_update(self):
        new, _ = core.merge_ask(b"{}", ["a", "b"], [])
        new, owned = core.merge_ask(new, ["a"], ["a", "b"])
        self.assertEqual(json.loads(new)["permissions"]["ask"], ["a"])
        self.assertEqual(owned, ["a"])


class Generated(unittest.TestCase):
    def test_rule_shapes(self):
        claude = agents.claude_rules()
        self.assertIn("Bash(npm test *)", claude)
        self.assertIn("Bash(npm run test*)", claude)
        self.assertIn("command(npm run test)", agents.antigravity_rules())
        self.assertIn('pattern=["npm", "run", "test"]', agents.codex_rules_text())

    def test_every_skill_is_loadable(self):
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            self.assertIn(f"name: {path.parent.name}\n", text)
            self.assertIn("description: ", text)

    def test_tests_and_reports_are_manual(self):
        for name in ("pros-test-web", "pros-test-mobile", "pros-test-components", "pros-review",
                     "pros-audit", "pros-tokens"):
            self.assertIn("disable-model-invocation: true", (ROOT / "skills" / name / "SKILL.md").read_text())


class Sandbox(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        (self.home / ".claude").mkdir()
        (self.home / ".claude" / "CLAUDE.md").write_text(USER_CLAUDE)
        (self.home / ".claude" / "settings.json").write_text(USER_SETTINGS)
        (self.home / ".codex" / "rules").mkdir(parents=True)
        (self.home / ".codex" / "AGENTS.md").write_text("")
        (self.home / ".codex" / "rules" / "default.rules").write_text(USER_DEFAULT_RULES)
        (self.home / ".cursor").mkdir()
        (self.home / ".gemini" / "antigravity-cli").mkdir(parents=True)
        self.env = {**os.environ, "HOME": str(self.home), "USERPROFILE": str(self.home)}
        self.env.pop("CLAUDE_CONFIG_DIR", None)
        self.env.pop("CODEX_HOME", None)

    def tearDown(self):
        self.tmp.cleanup()

    def pros(self, *args, stdin=subprocess.DEVNULL):
        return subprocess.run([sys.executable, str(ROOT / "pros.py"), *args], env=self.env, cwd=str(self.home),
                              capture_output=True, text=True, stdin=stdin)

    def install(self, *extra):
        result = self.pros("install", "--agents", ALL, "--yes", "--skip-tools", "--skip-upstream", *extra)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_dry_run_changes_nothing(self):
        before = snapshot(self.home)
        result = self.pros("install", "--agents", ALL, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Dry run", result.stdout)
        self.assertEqual(snapshot(self.home), before)

    def test_refuses_without_terminal_or_yes(self):
        before = snapshot(self.home)
        result = self.pros("install", "--agents", ALL, "--skip-tools", "--skip-upstream")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(snapshot(self.home), before)

    def test_install_preserves_user_config(self):
        self.install()
        claude_md = (self.home / ".claude" / "CLAUDE.md").read_text()
        self.assertTrue(claude_md.startswith(USER_CLAUDE))
        self.assertIn(core.BLOCK_START, claude_md)
        settings = json.loads((self.home / ".claude" / "settings.json").read_text())
        self.assertEqual(settings["theme"], "dark")
        self.assertEqual(settings["permissions"]["allow"], ["Bash(ls)"])
        self.assertIn("Bash(rm *)", settings["permissions"]["ask"])
        self.assertIn("Bash(npm test *)", settings["permissions"]["ask"])
        self.assertEqual((self.home / ".codex" / "rules" / "default.rules").read_text(), USER_DEFAULT_RULES)

    def test_skills_reach_every_agent_folder(self):
        self.install()
        for folder in (".claude/skills", ".agents/skills", ".gemini/config/skills"):
            self.assertTrue((self.home / folder / "pros-plan" / "SKILL.md").is_file(), folder)
        yaml = self.home / ".agents/skills/pros-test-web/agents/openai.yaml"
        self.assertIn("allow_implicit_invocation: false", yaml.read_text())
        self.assertFalse((self.home / ".agents/skills/pros-graph/agents/openai.yaml").exists())
        rule = (self.home / ".gemini/config/rules/pros-toolkit.md").read_text()
        self.assertTrue(rule.startswith("---\ntrigger: always_on\n"))

    def test_install_twice_is_idempotent(self):
        self.install()
        first = snapshot(self.home / ".claude")
        self.install()
        self.assertEqual(snapshot(self.home / ".claude"), first)

    def test_existing_skill_is_not_overwritten(self):
        mine = self.home / ".claude" / "skills" / "pros-plan"
        mine.mkdir(parents=True)
        (mine / "SKILL.md").write_text("mine")
        result = self.install()
        self.assertIn("kept your existing", result.stdout)
        self.assertEqual((mine / "SKILL.md").read_text(), "mine")
        self.assertEqual(self.pros("uninstall", "--yes").returncode, 0)
        self.assertEqual((mine / "SKILL.md").read_text(), "mine")

    def test_malformed_settings_stop_the_install(self):
        path = self.home / ".claude" / "settings.json"
        path.write_text("{broken")
        before = snapshot(self.home)
        result = self.pros("install", "--agents", ALL, "--yes", "--skip-tools", "--skip-upstream")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(snapshot(self.home), before)

    def test_uninstall_restores_exact_bytes(self):
        before = snapshot(self.home)
        self.install()
        result = self.pros("uninstall", "--yes")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(snapshot(self.home), before)

    def test_uninstall_keeps_later_user_edits(self):
        self.install()
        path = self.home / ".claude" / "CLAUDE.md"
        path.write_text(path.read_text() + "\nAdded later.\n")
        self.pros("uninstall", "--yes")
        text = path.read_text()
        self.assertIn("Keep this exactly.", text)
        self.assertIn("Added later.", text)
        self.assertNotIn(core.BLOCK_START, text)

    def test_interrupted_install_can_still_be_uninstalled(self):
        before = snapshot(self.home)
        script = (
            f"import sys; sys.path.insert(0, {str(ROOT)!r})\n"
            "import pros_toolkit.install as i\n"
            "def stop(*a, **k): raise KeyboardInterrupt\n"
            "i.install_pypi = stop\n"
            "from pros_toolkit.cli import main\n"
            f"sys.exit(main(['install', '--agents', {ALL!r}, '--yes', '--skip-upstream']))\n"
        )
        crashed = subprocess.run([sys.executable, "-c", script], env=self.env, cwd=str(self.home),
                                 capture_output=True, text=True)
        self.assertNotEqual(crashed.returncode, 0)
        self.assertIn(core.BLOCK_START, (self.home / ".claude" / "CLAUDE.md").read_text())
        self.assertEqual(self.pros("uninstall", "--yes").returncode, 0)
        self.assertEqual(snapshot(self.home), before)

    def test_init_adds_and_removes_cursor_rule(self):
        repo = self.home / "repo"
        repo.mkdir()
        self.assertEqual(self.pros("init", str(repo)).returncode, 0)
        rule = repo / ".cursor" / "rules" / "pros-toolkit.mdc"
        self.assertIn("alwaysApply: true", rule.read_text())
        self.assertEqual(self.pros("init", str(repo), "--remove").returncode, 0)
        self.assertFalse(rule.exists())


if __name__ == "__main__":
    unittest.main()
