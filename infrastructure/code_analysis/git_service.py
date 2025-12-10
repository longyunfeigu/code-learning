"""Git 服务模块 - 仓库克隆和管理.

提供 Git 仓库的克隆、更新和版本管理功能，是代码分析与索引的前置能力。
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit

from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class RepoInfo:
    """仓库信息"""

    url: str
    local_path: str
    default_branch: str
    last_commit: str
    last_commit_date: Optional[datetime] = None
    clone_depth: Optional[int] = None


class GitService:
    """
    Git 服务

    提供仓库克隆、更新和基本信息获取功能。
    """

    def __init__(
        self,
        workspace_dir: Optional[str] = None,
        default_depth: Optional[int] = None,
    ) -> None:
        """初始化 Git 服务.

        Args:
            workspace_dir: 工作目录，存放克隆的仓库
            default_depth: 默认克隆深度，None 时使用配置中的值
        """

        self.workspace_dir = Path(workspace_dir or settings.git.workspace_dir).resolve()
        self.default_depth = default_depth or settings.git.default_clone_depth
        self.clone_timeout = settings.git.clone_timeout
        # 仓库大小上限（字节），用于防止资源耗尽
        self.max_repo_size_bytes = getattr(settings.git, "max_repo_size_mb", 500) * 1024 * 1024

        # 确保工作目录存在
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    async def clone_repo(
        self,
        repo_url: str,
        target_name: Optional[str] = None,
        depth: Optional[int] = None,
        branch: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> RepoInfo:
        """
        克隆仓库

        Args:
            repo_url: 仓库 URL
            target_name: 目标目录名，不指定则从 URL 提取
            depth: 克隆深度，None 表示完整克隆
            branch: 指定分支/Tag
            access_token: 私有仓库访问 token（仅用于 HTTPS，不会写入日志）

        Returns:
            RepoInfo: 仓库信息

        Raises:
            GitCloneError: 克隆失败时抛出
        """
        target_name = self._sanitize_target_name(target_name or self._extract_repo_name(repo_url))
        local_path = self.workspace_dir / target_name
        depth = depth if depth is not None else self.default_depth

        # 构造真实 clone URL（私有仓库 token 仅用于命令，不进入日志）
        clone_url = self._build_clone_url(repo_url, access_token)
        safe_url_for_log = self._sanitize_url_for_log(repo_url)

        logger.info(
            "cloning_repo",
            url=safe_url_for_log,
            target=str(local_path),
            depth=depth,
        )

        # 如果目录已存在，先删除
        if local_path.exists():
            shutil.rmtree(local_path)

        # 构建 git clone 命令
        cmd = ["git", "clone"]

        if depth and depth > 0:
            cmd.extend(["--depth", str(depth)])

        if branch:
            cmd.extend(["--branch", branch])

        cmd.extend([clone_url, str(local_path)])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.clone_timeout,
            )

            if result.returncode != 0:
                logger.error(
                    "git_clone_failed",
                    url=safe_url_for_log,
                    stderr=result.stderr,
                )
                raise GitCloneError("Clone failed", code="REPO_CLONE_FAILED", detail=result.stderr)

        except subprocess.TimeoutExpired:
            logger.error("git_clone_timeout", url=safe_url_for_log)
            raise GitCloneError("Clone timeout", code="REPO_CLONE_TIMEOUT")

        # 克隆完成后检查仓库大小，防止异常大仓库占满磁盘
        size_bytes = self._calculate_repo_size(local_path)
        if size_bytes > self.max_repo_size_bytes:
            logger.error(
                "repo_too_large",
                path=str(local_path),
                size=size_bytes,
                max_size=self.max_repo_size_bytes,
            )
            shutil.rmtree(local_path, ignore_errors=True)
            raise GitCloneError("Repository too large", code="REPO_TOO_LARGE")

        # 获取仓库信息
        repo_info = await self._get_repo_info(local_path, repo_url, depth)

        logger.info(
            "repo_cloned",
            url=safe_url_for_log,
            branch=repo_info.default_branch,
            commit=repo_info.last_commit[:8],
        )

        return repo_info

    async def update_repo(self, local_path: str) -> RepoInfo:
        """
        更新仓库（git pull）

        Args:
            local_path: 本地仓库路径

        Returns:
            RepoInfo: 更新后的仓库信息
        """
        path = Path(local_path)

        if not (path / ".git").exists():
            raise GitOperationError(f"Not a git repository: {local_path}")

        logger.info("updating_repo", path=local_path)

        result = subprocess.run(
            ["git", "pull"],
            cwd=path,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error("git_pull_failed", stderr=result.stderr)
            raise GitOperationError(f"Pull failed: {result.stderr}")

        return await self._get_repo_info(path)

    async def get_file_content(
        self,
        local_path: str,
        file_path: str,
        ref: Optional[str] = None,
    ) -> str:
        """
        获取文件内容

        Args:
            local_path: 仓库本地路径
            file_path: 文件相对路径
            ref: Git 引用 (commit/branch/tag)

        Returns:
            str: 文件内容
        """
        path = Path(local_path)

        if ref:
            # 从特定版本获取
            result = subprocess.run(
                ["git", "show", f"{ref}:{file_path}"],
                cwd=path,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise FileNotFoundError(f"File not found: {file_path} at {ref}")
            return result.stdout
        else:
            # 从工作目录获取
            full_path = path / file_path
            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            return full_path.read_text(encoding="utf-8")

    async def list_files(
        self,
        local_path: str,
        pattern: Optional[str] = None,
        exclude_dirs: Optional[list] = None,
    ) -> list:
        """
        列出仓库中的文件

        Args:
            local_path: 仓库本地路径
            pattern: 文件名模式 (glob)
            exclude_dirs: 排除的目录

        Returns:
            list: 文件路径列表
        """
        path = Path(local_path)
        exclude_dirs = exclude_dirs or [".git", "node_modules", "__pycache__", ".venv"]

        files = []
        for item in path.rglob(pattern or "*"):
            if item.is_file():
                # 检查是否在排除目录中
                parts = item.relative_to(path).parts
                if not any(d in parts for d in exclude_dirs):
                    files.append(str(item.relative_to(path)))

        return files

    async def _get_repo_info(
        self,
        local_path: Path,
        repo_url: Optional[str] = None,
        depth: Optional[int] = None,
    ) -> RepoInfo:
        """获取仓库信息"""
        # 获取默认分支
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=local_path,
            capture_output=True,
            text=True,
        )
        default_branch = result.stdout.strip() if result.returncode == 0 else "main"

        # 获取最新 commit
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=local_path,
            capture_output=True,
            text=True,
        )
        last_commit = result.stdout.strip() if result.returncode == 0 else ""

        # 获取 commit 时间
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci"],
            cwd=local_path,
            capture_output=True,
            text=True,
        )
        commit_date = None
        if result.returncode == 0 and result.stdout.strip():
            try:
                commit_date = datetime.fromisoformat(
                    result.stdout.strip().replace(" ", "T").replace(" +", "+")
                )
            except ValueError:
                pass

        # 获取远程 URL（如果没有提供）
        if not repo_url:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=local_path,
                capture_output=True,
                text=True,
            )
            repo_url = result.stdout.strip() if result.returncode == 0 else ""

        return RepoInfo(
            url=repo_url,
            local_path=str(local_path),
            default_branch=default_branch,
            last_commit=last_commit,
            last_commit_date=commit_date,
            clone_depth=depth,
        )

    def _extract_repo_name(self, url: str) -> str:
        """从 URL 或本地路径提取仓库名。"""
        name = url.rstrip("/")
        # 移除 .git 后缀
        if name.endswith(".git"):
            name = name[:-4]

        name = name.split("/")[-1]
        return name or "repo"

    def _sanitize_target_name(self, target_name: str) -> str:
        """清洗本地目标目录名，防止路径穿越。"""

        name = target_name.strip().replace("\\", "/")
        # 不允许绝对路径或包含 ..
        if name.startswith("/"):
            raise GitOperationError("Absolute paths are not allowed for target_name")
        if any(part == ".." for part in Path(name).parts):
            raise GitOperationError("target_name contains invalid path segment '..'")
        return name

    def _build_clone_url(self, repo_url: str, access_token: Optional[str]) -> str:
        """构造用于 git clone 的 URL，支持私有仓库 token.

        token 只出现在实际命令中，不会写入日志。
        """

        if not access_token:
            return repo_url

        # 仅对 HTTPS URL 注入 token，SSH/本地路径保持不变
        if repo_url.startswith("https://"):
            parsed = urlsplit(repo_url)
            netloc = parsed.netloc
            # 去除原有的 userinfo
            if "@" in netloc:
                netloc = netloc.split("@", 1)[-1]
            netloc = f"x-access-token:{access_token}@{netloc}"
            return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))

        return repo_url

    def _sanitize_url_for_log(self, url: str) -> str:
        """移除 URL 中的敏感信息，仅用于日志输出。"""

        try:
            parsed = urlsplit(url)
            netloc = parsed.netloc
            # 丢弃 userinfo
            if "@" in netloc:
                netloc = netloc.split("@", 1)[-1]
            return urlunsplit((parsed.scheme, netloc, parsed.path, "", ""))
        except Exception:
            return url

    def _calculate_repo_size(self, local_path: Path) -> int:
        """计算仓库占用的总字节数。"""

        total = 0
        for root, _dirs, files in os.walk(local_path):
            for filename in files:
                try:
                    fp = Path(root) / filename
                    total += fp.stat().st_size
                except OSError:
                    continue
        return total


class GitCloneError(Exception):
    """Git 克隆错误。"""

    def __init__(
        self, message: str, code: str = "GIT_CLONE_ERROR", detail: Optional[str] = None
    ) -> None:
        super().__init__(message)
        self.code = code
        self.detail = detail


class GitOperationError(Exception):
    """Git 操作错误。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
