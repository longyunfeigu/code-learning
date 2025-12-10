"""Git 相关 Celery 任务.

用于在后台克隆代码仓库并为后续代码分析做准备。
"""

from __future__ import annotations

from typing import Optional

from celery import shared_task

from core.logging_config import get_logger
from infrastructure.code_analysis.git_service import GitService, GitCloneError
from ..utils.base_task import BaseTask

logger = get_logger(__name__)


@shared_task(
    bind=True,
    base=BaseTask,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def clone_repository_task(
    self,
    repo_url: str,
    *,
    target_name: Optional[str] = None,
    depth: Optional[int] = None,
    branch: Optional[str] = None,
    access_token: Optional[str] = None,
) -> dict:
    """克隆 Git 仓库的异步任务。

    任务会在后台执行 `git clone`，并返回克隆后的元数据，用于后续代码分析。
    进度信息通过 `update_state` 进行简单上报，便于前端轮询。
    """

    git_service = GitService()

    # 标记任务开始，方便调用方感知状态
    self.update_state(state="PROGRESS", meta={"stage": "cloning"})

    try:
        repo_info = _run_clone(
            git_service=git_service,
            repo_url=repo_url,
            target_name=target_name,
            depth=depth,
            branch=branch,
            access_token=access_token,
        )
    except GitCloneError as exc:
        # Git 相关错误不再重试，直接失败返回业务错误码
        logger.error(
            "git_clone_task_failed",
            url=git_service._sanitize_url_for_log(repo_url),  # noqa: SLF001 - 内部安全调用
            code=getattr(exc, "code", None),
            detail=getattr(exc, "detail", None),
        )
        raise

    result = {
        "url": repo_info.url,
        "local_path": repo_info.local_path,
        "default_branch": repo_info.default_branch,
        "last_commit": repo_info.last_commit,
        "last_commit_date": (
            repo_info.last_commit_date.isoformat() if repo_info.last_commit_date else None
        ),
        "clone_depth": repo_info.clone_depth,
    }

    # 最终状态
    self.update_state(state="SUCCESS", meta={"stage": "completed"})
    return result


def _run_clone(
    *,
    git_service: GitService,
    repo_url: str,
    target_name: Optional[str],
    depth: Optional[int],
    branch: Optional[str],
    access_token: Optional[str],
):
    """实际执行克隆逻辑的辅助函数，便于在同步 Celery 任务中调用异步服务。"""

    import asyncio

    return asyncio.run(
        git_service.clone_repo(
            repo_url=repo_url,
            target_name=target_name,
            depth=depth,
            branch=branch,
            access_token=access_token,
        )
    )
