"""Exercise workspace CLI contracts against disposable Git and filesystem state."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "workspace.py"


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="workspace-operations-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "workspace"
        self.root.mkdir()
        self.env = {
            **os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_COUNT": "0", "GIT_AUTHOR_NAME": "Fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid", "GIT_COMMITTER_NAME": "Fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        }

    def git(self, repo, *args):
        return subprocess.run(
            ["git", "-C", str(repo), *args], env=self.env, check=True,
            capture_output=True, text=True,
        ).stdout.strip()

    def source_repo(self):
        repo = self.root / "source"
        repo.mkdir()
        self.git(repo, "init", "-b", "main")
        (repo / "source.txt").write_text("first\n")
        self.git(repo, "add", ".")
        self.git(repo, "commit", "-m", "first")
        first = self.git(repo, "rev-parse", "HEAD")
        (repo / "source.txt").write_text("second\n")
        self.git(repo, "commit", "-am", "second")
        return repo, first

    def command(self, *args, success=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), *args],
            cwd=self.base, env=self.env, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        receipt = json.loads(result.stdout)
        if not success:
            self.assertIn("error", receipt)
            self.assertTrue(result.stderr.strip())
        return receipt

    def test_requested_ref_branch_and_relative_worktree_links(self):
        repo, first = self.source_repo()
        (self.root / "repositories.json").write_text(
            json.dumps({"repositories": {"engine": "source"}})
        )
        result = self.command(
            "--config", "repositories.json", "worktree-add", "engine",
            "tasks/detached", "--ref", first,
        )
        detached = self.root / "tasks/detached"
        self.assertEqual(result["repository"], "source")
        self.assertEqual(self.git(detached, "rev-parse", "HEAD"), first)
        self.assertEqual(self.git(detached, "branch", "--show-current"), "")
        self.assertEqual((detached / "source.txt").read_text(), "first\n")
        git_link = (detached / ".git").read_text().strip().removeprefix("gitdir: ")
        self.assertFalse(Path(git_link).is_absolute())
        self.assertTrue((detached / git_link).resolve().is_dir())
        self.command("worktree-add", "source", "tasks/branch", "--branch", "experiment")
        worktree = self.root / "tasks/branch"
        self.assertEqual(self.git(worktree, "rev-parse", "HEAD"), self.git(repo, "rev-parse", "main"))
        self.assertEqual(self.git(worktree, "branch", "--show-current"), "experiment")
        self.command("worktree-remove", "source", "tasks/branch")
        self.assertFalse(worktree.exists())
        self.assertEqual(self.git(repo, "rev-parse", "experiment"), self.git(repo, "rev-parse", "main"))
        self.assertNotIn(str(worktree), self.git(repo, "worktree", "list", "--porcelain"))

    def test_dirty_worktree_dry_run_and_force_preserve_native_git_contract(self):
        repo, _ = self.source_repo()
        self.command("worktree-add", "source", "tasks/dirty", "--branch", "unfinished")
        worktree = self.root / "tasks/dirty"
        (worktree / "source.txt").write_text("unfinished edit\n")
        before = self.git(repo, "worktree", "list", "--porcelain")
        result = self.command("worktree-remove", "source", "tasks/dirty", "--dry-run")
        self.assertTrue(result["dry_run"])
        self.assertEqual((worktree / "source.txt").read_text(), "unfinished edit\n")
        self.assertEqual(self.git(repo, "worktree", "list", "--porcelain"), before)
        self.command("worktree-remove", "source", "tasks/dirty", success=False)
        self.assertTrue(worktree.exists())
        self.assertEqual(self.git(repo, "worktree", "list", "--porcelain"), before)
        self.command("worktree-remove", "source", "tasks/dirty", "--force")
        self.assertFalse(worktree.exists())
        self.assertEqual(self.git(repo, "rev-parse", "unfinished"), self.git(repo, "rev-parse", "main"))

    def test_task_metadata_and_links_remain_relative_to_task(self):
        self.command(
            "task-init", "tasks/experiment", "--title", "Experiment",
            "--records", "records/experiment", "--results", "results/experiment",
        )
        task = self.root / "tasks/experiment"
        metadata = json.loads((task / "task.json").read_text())
        self.assertEqual(metadata["title"], "Experiment")
        for name in ("records", "results"):
            target = self.root / name / "experiment"
            self.assertTrue((task / name).is_symlink())
            self.assertFalse(Path(os.readlink(task / name)).is_absolute())
            self.assertFalse(Path(metadata["paths"][name]).is_absolute())
            self.assertEqual((task / name).resolve(), target.resolve())
            self.assertEqual((task / metadata["paths"][name]).resolve(), target.resolve())
            (task / name / "observation.txt").write_text(name)
            self.assertEqual((target / "observation.txt").read_text(), name)
        original = (task / "task.json").read_bytes()
        self.command("task-init", "tasks/experiment", "--title", "Replacement", success=False)
        self.assertEqual((task / "task.json").read_bytes(), original)
        self.assertEqual((task / "records/observation.txt").read_text(), "records")

    def test_task_collision_is_detected_before_new_targets_or_metadata(self):
        for kind in ("owned-file", "dangling-link"):
            with self.subTest(kind=kind):
                task = self.root / "tasks" / kind
                task.mkdir(parents=True)
                occupied = task / "results"
                if kind == "owned-file":
                    occupied.write_text("user data")
                else:
                    occupied.symlink_to("missing-target", target_is_directory=True)
                self.command(
                    "task-init", f"tasks/{kind}", "--records", f"new-records/{kind}",
                    "--results", f"new-results/{kind}", success=False,
                )
                self.assertFalse((task / "task.json").exists())
                self.assertFalse((self.root / "new-records").exists())
                self.assertFalse((self.root / "new-results").exists())
                if kind == "owned-file":
                    self.assertEqual(occupied.read_text(), "user data")
                else:
                    self.assertEqual(os.readlink(occupied), "missing-target")

    def test_directory_removal_dry_run_and_symlink_preserve_target(self):
        target = self.base / "results"
        target.mkdir()
        (target / "owned.txt").write_text("keep")
        link = self.root / "results"
        link.symlink_to("../results", target_is_directory=True)
        self.command("directory-remove", "results", "--dry-run")
        self.assertTrue(link.is_symlink())
        self.command("directory-remove", "results")
        self.assertFalse(os.path.lexists(link))
        self.assertEqual((target / "owned.txt").read_text(), "keep")
        directory = self.root / "discard"
        directory.mkdir()
        (directory / "scratch").write_text("temporary")
        self.command("directory-remove", "discard", "--dry-run")
        self.assertEqual((directory / "scratch").read_text(), "temporary")
        self.command("directory-remove", "discard")
        self.assertFalse(directory.exists())

    def test_directory_removal_rejects_workspace_root_and_ancestors(self):
        (self.root / "owned.txt").write_text("keep workspace")
        for directory in (".", ".."):
            with self.subTest(directory=directory):
                self.command("directory-remove", directory, success=False)
                self.assertEqual((self.root / "owned.txt").read_text(), "keep workspace")


if __name__ == "__main__":
    unittest.main()
