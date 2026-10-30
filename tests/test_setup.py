"""Bootstrap checks that protect a task's existing files; no network or Codex calls."""
from pathlib import Path
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "setup.sh"


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="playbook-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.task = self.root / "과제 with spaces"
        self.task.mkdir()
        (self.task / "README.md").write_text("# Original task\nKeep this file.\n")
        (self.task / "answer.txt").write_text("existing solution\n")

    def run_setup(self, *args, success=True):
        result = subprocess.run(
            ["bash", str(SCRIPT), *map(str, args)],
            text=True, capture_output=True, cwd=self.root,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def snapshot(self):
        return {
            str(p.relative_to(self.task)): (
                "link", str(p.readlink())
            ) if p.is_symlink() else ("dir",) if p.is_dir() else (
                "file", p.read_bytes(), p.stat().st_mtime_ns
            )
            for p in self.task.rglob("*")
        }

    def test_setup_preserves_task_and_is_repeatable(self):
        original = self.snapshot()
        self.run_setup(self.task)
        for path, value in original.items():
            self.assertEqual(self.snapshot()[path], value)
        bundle = self.task / ".codex-playbook"
        for name in ("AGENTS.md", "PLAYBOOK.md", "QUICKSTART.md", "UI_ASSETS.md"):
            self.assertEqual((bundle / name).read_bytes(), (REPO / name).read_bytes())
        self.assertEqual(
            (bundle / "START_PROMPT.txt").read_bytes(),
            (REPO / "prompts" / "start.txt").read_bytes(),
        )
        self.assertIn(".codex-playbook/AGENTS.md", (self.task / "AGENTS.md").read_text())
        first = self.snapshot()
        self.run_setup(self.task)
        self.assertEqual(first, self.snapshot())

    def test_check_writes_nothing(self):
        before = self.snapshot()
        self.run_setup("--check", self.task)
        self.assertEqual(before, self.snapshot())

    def test_existing_agents_are_preserved(self):
        for name in ("AGENTS.md", "AGENTS.override.md"):
            (self.task / name).write_text("# Keep project-specific rules\n")
        before = self.snapshot()
        self.run_setup(self.task)
        for name in ("AGENTS.md", "AGENTS.override.md"):
            self.assertEqual(before[name], self.snapshot()[name])

    def test_override_alone_does_not_create_root_agents(self):
        (self.task / "AGENTS.override.md").write_text("# Existing override\n")
        self.run_setup(self.task)
        self.assertFalse((self.task / "AGENTS.md").exists())

    def test_conflicting_bundle_is_untouched(self):
        bundle = self.task / ".codex-playbook"
        bundle.mkdir()
        (bundle / "PLAYBOOK.md").write_text("custom work\n")
        before = self.snapshot()
        self.run_setup(self.task, success=False)
        self.assertEqual(before, self.snapshot())

    def test_symlink_bundle_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.task / ".codex-playbook").symlink_to(outside, target_is_directory=True)
        before = self.snapshot()
        self.run_setup(self.task, success=False)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(list(outside.iterdir()), [])

    def test_symlink_file_is_rejected(self):
        bundle = self.task / ".codex-playbook"
        bundle.mkdir()
        outside = self.root / "untouched.md"
        outside.write_text("unchanged\n")
        (bundle / "AGENTS.md").symlink_to(outside)
        before = self.snapshot()
        self.run_setup(self.task, success=False)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(outside.read_text(), "unchanged\n")

    def test_missing_readme_is_rejected_without_writes(self):
        (self.task / "README.md").unlink()
        before = self.snapshot()
        self.run_setup(self.task, success=False)
        self.assertEqual(before, self.snapshot())

    def test_invalid_targets_and_arguments_fail(self):
        self.run_setup(success=False)
        self.run_setup(self.root / "missing", success=False)
        self.run_setup(REPO, success=False)
        self.run_setup("/", success=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
