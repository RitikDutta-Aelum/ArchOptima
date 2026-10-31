"""Installer regression checks: correct discovery paths and safe file handling."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "install.py"
SPEC = importlib.util.spec_from_file_location("architecture_install", SCRIPT)
installer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = installer
SPEC.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "SKILL.md").write_text(
            "---\nname: architecture-advisor\ndescription: Review architectures.\n---\n# Review\n",
            encoding="utf-8",
        )
        (self.source / "references").mkdir()
        (self.source / "references" / "workflow.md").write_text("Evidence first.\n", encoding="utf-8")
        self.target = self.root / "host" / "skills"

    def tearDown(self):
        self.temporary.cleanup()

    def test_all_harness_destinations(self):
        expected = {
            "codex": (".agents/skills", ".agents/skills"),
            "agents": (".agents/skills", ".agents/skills"),
            "claude": (".claude/skills", ".claude/skills"),
            "cursor": (".cursor/skills", ".cursor/skills"),
            "copilot": (".github/skills", ".copilot/skills"),
            "gemini": (".gemini/skills", ".gemini/skills"),
        }
        for harness, (project_suffix, user_suffix) in expected.items():
            with self.subTest(harness=harness):
                project = installer.choose_target(harness=harness, scope="project",
                                                  project=self.root, target=None)
                user = installer.choose_target(harness=harness, scope="user",
                                               project=None, target=None, home=self.root)
                self.assertEqual(project, self.root / project_suffix)
                self.assertEqual(user, self.root / user_suffix)

    def test_preview_cli_changes_nothing(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--source", str(self.source),
                                 "--target", str(self.target)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "preview")
        self.assertFalse(self.target.parent.exists())

    def test_copy_keeps_resources_and_ignores_python_cache(self):
        (self.source / "__pycache__").mkdir()
        (self.source / "__pycache__" / "cache.pyc").write_bytes(b"cache")
        plan = installer.plan_install(self.source, self.target)
        self.assertEqual(plan.files, 2)
        installer.apply_install(plan)
        destination = Path(plan.destination)
        self.assertEqual((destination / "references" / "workflow.md").read_text(), "Evidence first.\n")
        self.assertFalse((destination / "__pycache__").exists())
        self.assertTrue((self.source / "SKILL.md").exists())

    def test_refuse_overwrite_preserves_existing_content(self):
        destination = self.target / "architecture-advisor"
        destination.mkdir(parents=True)
        marker = destination / "important.txt"
        marker.write_text("keep me", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            installer.plan_install(self.source, self.target)
        self.assertEqual(marker.read_text(), "keep me")

    def test_refuse_nested_destination(self):
        with self.assertRaises(ValueError):
            installer.plan_install(self.source, self.source / "nested")

    def test_refuse_unsafe_name(self):
        (self.source / "SKILL.md").write_text("---\nname: ../../outside\n---\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            installer.plan_install(self.source, self.target)

    def test_refuse_source_symlink(self):
        link = self.source / "secret.txt"
        try:
            link.symlink_to(self.root / "outside.txt")
        except (OSError, NotImplementedError):
            self.skipTest("This platform does not allow symlink creation.")
        with self.assertRaises(ValueError):
            installer.plan_install(self.source, self.target)

    def test_refuse_broken_destination_symlink(self):
        self.target.mkdir(parents=True)
        try:
            (self.target / "architecture-advisor").symlink_to(self.root / "missing")
        except (OSError, NotImplementedError):
            self.skipTest("This platform does not allow symlink creation.")
        with self.assertRaises(FileExistsError):
            installer.plan_install(self.source, self.target)

    def test_project_must_be_explicit(self):
        with self.assertRaises(ValueError):
            installer.choose_target(harness="codex", scope="project", project=None, target=None)

    def test_no_ambiguous_target_combination(self):
        with self.assertRaises(ValueError):
            installer.choose_target(harness=None, scope="user", project=None, target=self.target)

    def test_source_mutation_prevents_install(self):
        plan = installer.plan_install(self.source, self.target)
        (self.source / "new-file.txt").write_text("Changed source", encoding="utf-8")
        with self.assertRaises(ValueError):
            installer.apply_install(plan)
        self.assertFalse(self.target.exists())

    def test_cleanup_on_copy_failure(self):
        from unittest.mock import patch
        plan = installer.plan_install(self.source, self.target)
        with patch.object(installer.shutil, "copytree", side_effect=OSError("simulated copy failure")):
            with self.assertRaises(OSError):
                installer.apply_install(plan)
        self.assertFalse(Path(plan.destination).exists())
        self.assertTrue(self.source.exists())


if __name__ == "__main__":
    unittest.main()
