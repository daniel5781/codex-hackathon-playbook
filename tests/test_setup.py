"""Bootstrap checks that protect a task's existing files; no network or Codex calls."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "setup.sh"
BASH = shutil.which("bash")
DOCUMENTS = (
    "AGENTS.md", "PLAYBOOK.md", "OPTIMIZATION.md", "PROCESS_OPTIMIZATION.md",
    "PROCESS_REFERENCE.md", "QUICKSTART.md", "UI_ASSETS.md", "VERIFICATION.md",
)
# 배치된 파일 이름 -> prompts/ 아래 원본 이름
PROMPTS = {
    "START_PROMPT.txt": "start.txt",
    "PROCESS_OPTIMIZATION_PROMPTS.txt": "process-optimization.txt",
}


@unittest.skipUnless(BASH, "Bash is required to exercise setup.sh")
class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="playbook-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.task = self.root / "과제 with spaces"
        self.task.mkdir()
        (self.task / "README.md").write_text("# Original task\nKeep this file.\n", encoding="utf-8")
        (self.task / "answer.txt").write_text("existing solution\n", encoding="utf-8")

    def run_setup(self, *args, success=True, script=SCRIPT):
        result = subprocess.run(
            [BASH, str(script), *map(str, args)],
            text=True, encoding="utf-8", capture_output=True, cwd=self.root,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def make_symlink(self, link, target, **kwargs):
        try:
            link.symlink_to(target, **kwargs)
        except OSError as exc:
            if getattr(exc, "winerror", None) == 1314:
                self.skipTest("Windows did not grant the privilege required to create symlinks")
            raise

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
        self.run_setup("--apply", self.task)
        for path, value in original.items():
            self.assertEqual(self.snapshot()[path], value)
        bundle = self.task / ".codex-playbook"
        for name in DOCUMENTS:
            self.assertEqual((bundle / name).read_bytes(), (REPO / name).read_bytes())
        for placed, original_name in PROMPTS.items():
            self.assertEqual(
                (bundle / placed).read_bytes(),
                (REPO / "prompts" / original_name).read_bytes(),
            )
        self.assertEqual(
            sorted(p.name for p in bundle.iterdir()), sorted((*DOCUMENTS, *PROMPTS)),
        )
        self.assertIn(".codex-playbook/AGENTS.md", (self.task / "AGENTS.md").read_text(encoding="utf-8"))
        first = self.snapshot()
        self.run_setup("--apply", self.task)
        self.assertEqual(first, self.snapshot())

    def test_generated_bridge_links_resolve(self):
        self.run_setup("--apply", self.task)
        bridge = (self.task / "AGENTS.md").read_text(encoding="utf-8")
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", bridge)
        for name in (
            "AGENTS.md", "PLAYBOOK.md", "OPTIMIZATION.md", "PROCESS_OPTIMIZATION.md",
            "UI_ASSETS.md", "VERIFICATION.md",
        ):
            self.assertIn(f".codex-playbook/{name}", links)
        for link in links:
            with self.subTest(link=link):
                self.assertTrue((self.task / link).is_file())

    def test_utf8_output_with_cp949_process_default(self):
        real_popen = subprocess.Popen

        def cp949_default_popen(*args, **kwargs):
            # Simulate the Windows default only when no encoding is specified.
            kwargs.setdefault("encoding", "cp949")
            return real_popen(*args, **kwargs)

        with patch("subprocess.Popen", side_effect=cp949_default_popen):
            result = self.run_setup("--apply", self.task)
            self.assertIn("대상 과제:", result.stdout)
            self.assertIn("과제 with spaces", result.stdout)
            bridge = (self.task / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("# 프로젝트 작업 지침", bridge)
            failed = self.run_setup("--unknown", self.task, success=False)
            self.assertIn("사용법:", failed.stderr)

    def test_check_writes_nothing(self):
        before = self.snapshot()
        self.run_setup("--check", self.task)
        self.assertEqual(before, self.snapshot())

    def test_default_writes_nothing(self):
        before = self.snapshot()
        self.run_setup(self.task)
        self.assertEqual(before, self.snapshot())

    def test_invalid_modes_write_nothing(self):
        before = self.snapshot()
        for flags in (("--unknown",), ("--check", "--apply"), ("--apply", "--check")):
            with self.subTest(flags=flags):
                self.run_setup(*flags, self.task, success=False)
                self.assertEqual(before, self.snapshot())

    def test_existing_agents_are_preserved(self):
        for name in ("AGENTS.md", "AGENTS.override.md"):
            (self.task / name).write_text("# Keep project-specific rules\n", encoding="utf-8")
        before = self.snapshot()
        self.run_setup("--apply", self.task)
        for name in ("AGENTS.md", "AGENTS.override.md"):
            self.assertEqual(before[name], self.snapshot()[name])

    def test_override_alone_does_not_create_root_agents(self):
        (self.task / "AGENTS.override.md").write_text("# Existing override\n", encoding="utf-8")
        self.run_setup("--apply", self.task)
        self.assertFalse((self.task / "AGENTS.md").exists())

    def test_conflicting_bundle_is_untouched(self):
        bundle = self.task / ".codex-playbook"
        bundle.mkdir()
        (bundle / "PLAYBOOK.md").write_text("custom work\n", encoding="utf-8")
        before = self.snapshot()
        self.run_setup("--apply", self.task, success=False)
        self.assertEqual(before, self.snapshot())

    def test_optimization_conflict_stops_before_any_write(self):
        bundle = self.task / ".codex-playbook"
        bundle.mkdir()
        (bundle / "OPTIMIZATION.md").write_text("# Project-specific optimization rules\n", encoding="utf-8")
        before = self.snapshot()
        for mode in ("--check", "--apply"):
            with self.subTest(mode=mode):
                result = self.run_setup(mode, self.task, success=False)
                self.assertIn("OPTIMIZATION.md", result.stderr)
                self.assertEqual(before, self.snapshot())

    def test_missing_optimization_source_stops_before_any_write(self):
        source = self.root / "incomplete-playbook"
        (source / "scripts").mkdir(parents=True)
        (source / "prompts").mkdir()
        shutil.copy2(SCRIPT, source / "scripts" / "setup.sh")
        for name in DOCUMENTS:
            if name != "OPTIMIZATION.md":
                shutil.copy2(REPO / name, source / name)
        for original_name in PROMPTS.values():
            shutil.copy2(REPO / "prompts" / original_name, source / "prompts" / original_name)
        before = self.snapshot()
        for mode in ("--check", "--apply"):
            with self.subTest(mode=mode):
                result = self.run_setup(
                    mode, self.task, success=False, script=source / "scripts" / "setup.sh",
                )
                self.assertIn("원본 문서 누락: OPTIMIZATION.md", result.stderr)
                self.assertEqual(before, self.snapshot())

    def test_symlink_bundle_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.make_symlink(self.task / ".codex-playbook", outside, target_is_directory=True)
        before = self.snapshot()
        self.run_setup("--apply", self.task, success=False)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(list(outside.iterdir()), [])

    def test_symlink_file_is_rejected(self):
        bundle = self.task / ".codex-playbook"
        bundle.mkdir()
        outside = self.root / "untouched.md"
        outside.write_text("unchanged\n", encoding="utf-8")
        self.make_symlink(bundle / "AGENTS.md", outside)
        before = self.snapshot()
        self.run_setup("--apply", self.task, success=False)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(outside.read_text(encoding="utf-8"), "unchanged\n")

    def test_missing_readme_is_rejected_without_writes(self):
        (self.task / "README.md").unlink()
        before = self.snapshot()
        self.run_setup("--apply", self.task, success=False)
        self.assertEqual(before, self.snapshot())

    def test_invalid_targets_and_arguments_fail(self):
        self.run_setup(success=False)
        self.run_setup(self.root / "missing", success=False)
        self.run_setup(REPO, success=False)
        self.run_setup("/", success=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
