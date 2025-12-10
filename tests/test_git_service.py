"""Tests for :mod:`infrastructure.code_analysis.git_service`."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from infrastructure.code_analysis.git_service import GitService, GitCloneError, GitOperationError


def _init_local_repo(repo_dir: Path) -> None:
    """Create a minimal local git repository for testing."""

    repo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("GIT_AUTHOR_NAME", "tester")
    env.setdefault("GIT_AUTHOR_EMAIL", "tester@example.com")
    env.setdefault("GIT_COMMITTER_NAME", "tester")
    env.setdefault("GIT_COMMITTER_EMAIL", "tester@example.com")

    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True, env=env)
    (repo_dir / "foo.py").write_text(
        """class Foo:\n    def bar(self):\n        return 1\n""", encoding="utf-8"
    )
    subprocess.run(["git", "add", "foo.py"], cwd=repo_dir, check=True, capture_output=True, env=env)
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "init",
        ],
        cwd=repo_dir,
        check=True,
        capture_output=True,
        env=env,
    )


@pytest.mark.asyncio
async def test_clone_and_read_files(tmp_path: Path) -> None:
    """GitService should clone a local repository and list/read files."""

    source_repo = tmp_path / "source_repo"
    _init_local_repo(source_repo)

    workspace = tmp_path / "workspace"
    git_service = GitService(workspace_dir=str(workspace))

    repo_info = await git_service.clone_repo(str(source_repo))

    assert Path(repo_info.local_path).exists()

    files = await git_service.list_files(repo_info.local_path)
    assert "foo.py" in files

    content = await git_service.get_file_content(repo_info.local_path, "foo.py")
    assert "class Foo" in content


@pytest.mark.asyncio
async def test_clone_respects_size_limit(tmp_path: Path) -> None:
    """Clone should fail with REPO_TOO_LARGE when repo exceeds configured limit."""

    source_repo = tmp_path / "big_repo"
    _init_local_repo(source_repo)

    workspace = tmp_path / "workspace2"
    git_service = GitService(workspace_dir=str(workspace))
    # 强制设置极小的大小上限以触发限制逻辑
    git_service.max_repo_size_bytes = 1

    with pytest.raises(GitCloneError) as exc:
        await git_service.clone_repo(str(source_repo))

    assert exc.value.code == "REPO_TOO_LARGE"


@pytest.mark.asyncio
async def test_invalid_target_name_rejected(tmp_path: Path) -> None:
    """Unsafe target_name values must be rejected to avoid path traversal."""

    source_repo = tmp_path / "source_repo3"
    _init_local_repo(source_repo)

    workspace = tmp_path / "workspace3"
    git_service = GitService(workspace_dir=str(workspace))

    with pytest.raises(GitOperationError):
        await git_service.clone_repo(str(source_repo), target_name="../evil")
