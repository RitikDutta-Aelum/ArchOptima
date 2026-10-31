#!/usr/bin/env python3
"""Copy this complete Agent Skill into an explicitly selected local skills root.

Preview is the default. Add --apply to install. This script uses only the Python
standard library. It never downloads files, installs dependencies, edits harness
configuration, follows source symlinks, or replaces an existing destination.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
from dataclasses import asdict, dataclass


SKILL_NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
HARNESS_PATHS = {
    "agents": {"project": ".agents/skills", "user": ".agents/skills"},
    "codex": {"project": ".agents/skills", "user": ".agents/skills"},
    "claude": {"project": ".claude/skills", "user": ".claude/skills"},
    "cursor": {"project": ".cursor/skills", "user": ".cursor/skills"},
    "copilot": {"project": ".github/skills", "user": ".copilot/skills"},
    "gemini": {"project": ".gemini/skills", "user": ".gemini/skills"},
}
IGNORED_NAMES = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".DS_Store"}


@dataclass(frozen=True)
class InstallPlan:
    name: str
    source: str
    destination: str
    files: int
    bytes: int


def skill_name(source: Path) -> str:
    """Read a simple scalar name from frontmatter without a YAML dependency."""
    manifest = source / "SKILL.md"
    if not manifest.is_file() or manifest.is_symlink():
        raise ValueError("Source must contain a regular SKILL.md file.")
    if manifest.stat().st_size > 256 * 1024:
        raise ValueError("SKILL.md is unexpectedly large; inspect the source first.")
    text = manifest.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must begin with YAML frontmatter.")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("SKILL.md frontmatter has no closing delimiter.") from exc
    names = []
    for line in lines[1:end]:
        match = re.fullmatch(r"name:\s*(.*?)\s*", line)
        if match:
            value = match.group(1)
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            names.append(value)
    if len(names) != 1:
        raise ValueError("SKILL.md must have exactly one simple top-level name.")
    name = names[0]
    if len(name) > 64 or not SKILL_NAME_PATTERN.fullmatch(name):
        raise ValueError("Skill name must be 1-64 lowercase letters/digits separated by single hyphens.")
    return name


def source_inventory(source: Path) -> tuple[int, int]:
    """Validate regular files before copying; reject symlinks and special files."""
    count = total = 0
    for root, directories, filenames in os.walk(source, followlinks=False):
        directories[:] = [name for name in directories if name not in IGNORED_NAMES]
        for name in directories + filenames:
            if name in IGNORED_NAMES or name.endswith((".pyc", ".pyo")):
                continue
            path = Path(root) / name
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise ValueError(f"Source contains a symlink; use a self-contained copy: {path.relative_to(source)}")
            if stat.S_ISREG(mode):
                count += 1
                total += path.stat().st_size
            elif not stat.S_ISDIR(mode):
                raise ValueError(f"Source contains a non-regular entry: {path.relative_to(source)}")
    return count, total


def choose_target(*, harness: str | None, scope: str, project: Path | None,
                  target: Path | None, home: Path | None = None) -> Path:
    if target is not None:
        if harness is not None or project is not None or scope != "project":
            raise ValueError("Use --target alone, without --harness, --project, or --scope user.")
        return target.expanduser().resolve()
    if harness not in HARNESS_PATHS:
        raise ValueError("Choose --harness or an explicit --target skills parent directory.")
    if scope == "user":
        if project is not None:
            raise ValueError("--project applies only to project scope.")
        base = (home or Path.home()).expanduser().resolve()
    else:
        if project is None:
            raise ValueError("Project installation requires --project PATH.")
        base = project.expanduser().resolve()
        if not base.is_dir():
            raise ValueError("The project directory must already exist.")
    return base / HARNESS_PATHS[harness][scope]


def plan_install(source: Path, target: Path) -> InstallPlan:
    raw_source = source.expanduser()
    if raw_source.is_symlink():
        raise ValueError("Source root is a symlink; pass its real directory explicitly.")
    source = raw_source.resolve()
    if not source.is_dir():
        raise ValueError("Source skill directory does not exist.")
    name = skill_name(source)
    target = target.expanduser().resolve()
    if target.exists() and not target.is_dir():
        raise ValueError("Target skills parent exists and is not a directory.")
    destination = target / name
    if destination == source or source in destination.parents or destination in source.parents:
        raise ValueError("Source and destination must be separate, non-overlapping directories.")
    # lexists catches broken symlinks, which Path.exists() does not.
    if os.path.lexists(destination):
        raise FileExistsError(f"Destination already exists; nothing will be overwritten: {destination}")
    count, total = source_inventory(source)
    return InstallPlan(name, str(source), str(destination), count, total)


def apply_install(plan: InstallPlan) -> None:
    source, destination = Path(plan.source), Path(plan.destination)
    # Recheck immediately before writing, including the source inventory.
    checked = plan_install(source, destination.parent)
    if checked != plan:
        raise ValueError("Source changed after planning; run the installer again.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # mkdir(exist_ok=False) reserves a new directory without replacing any path.
    destination.mkdir(exist_ok=False)
    try:
        def ignored(_directory: str, names: list[str]) -> list[str]:
            return [name for name in names
                    if name in IGNORED_NAMES or name.endswith((".pyc", ".pyo"))]

        # Preserve any symlink introduced after the preflight instead of following
        # it; the post-copy inventory then rejects and removes the new install.
        shutil.copytree(source, destination, dirs_exist_ok=True, ignore=ignored, symlinks=True)
        source_inventory(destination)
        if skill_name(destination) != plan.name:
            raise ValueError("Copied skill did not pass the installation check.")
    except BaseException:
        # Only the new directory created by this call is removed on failure.
        shutil.rmtree(destination)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1],
                        help="Source skill folder; defaults to the folder containing this script.")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--harness", choices=sorted(HARNESS_PATHS))
    target.add_argument("--target", type=Path,
                        help="Custom skills parent. Installs under TARGET/<skill-name>/.")
    parser.add_argument("--scope", choices=("project", "user"), default="project")
    parser.add_argument("--project", type=Path,
                        help="Existing target project directory; required for project scope.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Perform the copy.")
    mode.add_argument("--dry-run", action="store_true", help="Preview only (the default).")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        target = choose_target(harness=args.harness, scope=args.scope,
                               project=args.project, target=args.target)
        plan = plan_install(args.source, target)
        if args.apply:
            apply_install(plan)
        result = asdict(plan)
        result["status"] = "installed" if args.apply else "preview"
        result["next_step"] = (
            "Verify discovery in the selected harness; Python dependencies are separate."
            if args.apply else "Add --apply to copy the skill. No files were changed."
        )
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Installation error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
