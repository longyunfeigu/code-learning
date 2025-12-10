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


@pytest.mark.asyncio
async def test_clone_real_github_repo(tmp_path: Path) -> None:
    """Test cloning a real GitHub repository: code-learning project."""

    workspace = tmp_path / "workspace_real"
    git_service = GitService(workspace_dir=str(workspace), default_depth=1)

    # Clone the real repository
    repo_url = "https://github.com/longyunfeigu/code-learning"
    repo_info = await git_service.clone_repo(repo_url)

    # Verify basic repository info
    assert repo_info is not None
    assert repo_info.url == repo_url
    assert repo_info.local_path is not None
    assert Path(repo_info.local_path).exists()
    assert (Path(repo_info.local_path) / ".git").exists()

    # Verify branch and commit info
    assert repo_info.default_branch is not None
    assert repo_info.last_commit is not None
    assert len(repo_info.last_commit) == 40  # Git commit hash length
    assert repo_info.last_commit_date is not None
    assert repo_info.clone_depth == 1

    # List files in the repository
    files = await git_service.list_files(repo_info.local_path)
    assert len(files) > 0
    # Check for common project files
    assert any("README" in f or "readme" in f for f in files) or any(
        ".py" in f for f in files
    ), "Should contain README or Python files"

    # Test reading a file (if README exists)
    readme_files = [f for f in files if "README" in f or "readme" in f]
    if readme_files:
        content = await git_service.get_file_content(repo_info.local_path, readme_files[0])
        assert content is not None
        assert len(content) > 0


@pytest.mark.asyncio
async def test_clone_real_repo_with_specific_branch(tmp_path: Path) -> None:
    """Test cloning a specific branch from a real repository."""

    workspace = tmp_path / "workspace_branch"
    git_service = GitService(workspace_dir=str(workspace), default_depth=1)

    repo_url = "https://github.com/longyunfeigu/code-learning"
    # Try to clone the main branch explicitly
    repo_info = await git_service.clone_repo(repo_url, branch="main")

    assert repo_info is not None
    assert Path(repo_info.local_path).exists()
    # Verify we're on the requested branch
    assert repo_info.default_branch == "main"


@pytest.mark.asyncio
async def test_clone_real_repo_full_depth(tmp_path: Path) -> None:
    """Test cloning a real repository with full history (no depth limit)."""

    workspace = tmp_path / "workspace_full"
    git_service = GitService(workspace_dir=str(workspace))

    repo_url = "https://github.com/longyunfeigu/code-learning"
    # Clone with full history by passing depth=0 (no --depth flag added)
    repo_info = await git_service.clone_repo(repo_url, depth=0)

    assert repo_info is not None
    assert Path(repo_info.local_path).exists()
    assert repo_info.clone_depth == 0  # Full clone (depth=0 means no depth limit)

    # Verify we can access commit history
    result = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=repo_info.local_path,
        capture_output=True,
        text=True,
        check=True,
    )
    commits = result.stdout.strip().split("\n")
    # Full clone should have multiple commits (code-learning has multiple commits)
    assert len(commits) >= 2, f"Expected multiple commits, got: {commits}"
