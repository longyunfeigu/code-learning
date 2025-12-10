"""
Git 服务模块 - 仓库克隆和管理

提供 Git 仓库的克隆、更新和版本管理功能。
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

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
        default_depth: int = 1,
    ):
        """
        初始化 Git 服务
        
        Args:
            workspace_dir: 工作目录，存放克隆的仓库
            default_depth: 默认克隆深度
        """
        self.workspace_dir = Path(workspace_dir or settings.git.workspace_dir)
        self.default_depth = default_depth
        
        # 确保工作目录存在
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
    
    async def clone_repo(
        self,
        repo_url: str,
        target_name: Optional[str] = None,
        depth: Optional[int] = None,
        branch: Optional[str] = None,
    ) -> RepoInfo:
        """
        克隆仓库
        
        Args:
            repo_url: 仓库 URL
            target_name: 目标目录名，不指定则从 URL 提取
            depth: 克隆深度，None 表示完整克隆
            branch: 指定分支
        
        Returns:
            RepoInfo: 仓库信息
        
        Raises:
            GitCloneError: 克隆失败时抛出
        """
        target_name = target_name or self._extract_repo_name(repo_url)
        local_path = self.workspace_dir / target_name
        depth = depth if depth is not None else self.default_depth
        
        logger.info(
            "cloning_repo",
            url=repo_url,
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
        
        cmd.extend([repo_url, str(local_path)])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 分钟超时
            )
            
            if result.returncode != 0:
                logger.error(
                    "git_clone_failed",
                    url=repo_url,
                    stderr=result.stderr,
                )
                raise GitCloneError(f"Clone failed: {result.stderr}")
            
        except subprocess.TimeoutExpired:
            logger.error("git_clone_timeout", url=repo_url)
            raise GitCloneError(f"Clone timeout for {repo_url}")
        
        # 获取仓库信息
        repo_info = await self._get_repo_info(local_path, repo_url, depth)
        
        logger.info(
            "repo_cloned",
            url=repo_url,
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
        """从 URL 提取仓库名"""
        # 移除 .git 后缀
        name = url.rstrip("/")
        if name.endswith(".git"):
            name = name[:-4]
        
        # 提取最后一部分
        name = name.split("/")[-1]
        
        return name


class GitCloneError(Exception):
    """Git 克隆错误"""
    pass


class GitOperationError(Exception):
    """Git 操作错误"""
    pass

