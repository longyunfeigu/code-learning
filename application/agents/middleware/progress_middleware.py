"""
进度跟踪中间件 - 跟踪学习进度和状态

职责：
- 记录学习阶段变化
- 跟踪问题完成状态
- 持久化进度数据
"""

from typing import Any, Dict, Optional
from datetime import datetime


class ProgressTrackingMiddleware:
    """
    进度跟踪中间件
    
    用于在 Agent 执行过程中跟踪学习进度，
    包括阶段进度、问题完成状态、时间统计等。
    """
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.project_id = project_id
        self._progress: Dict[str, Any] = {
            "current_stage": None,
            "completed_stages": [],
            "answered_questions": [],
            "correct_questions": [],
            "capability_progress": {},
            "total_time_spent": 0,
            "last_active_at": None,
        }
    
    @property
    def progress(self) -> Dict[str, Any]:
        """获取当前进度快照"""
        return self._progress.copy()
    
    def update_stage(self, stage_id: str) -> None:
        """更新当前学习阶段"""
        if self._progress["current_stage"] and self._progress["current_stage"] != stage_id:
            if self._progress["current_stage"] not in self._progress["completed_stages"]:
                self._progress["completed_stages"].append(self._progress["current_stage"])
        self._progress["current_stage"] = stage_id
        self._progress["last_active_at"] = datetime.utcnow().isoformat()
    
    def record_answer(
        self,
        question_id: str,
        is_correct: bool,
        time_spent: int,
        score: Optional[float] = None,
    ) -> None:
        """记录问题回答"""
        if question_id not in self._progress["answered_questions"]:
            self._progress["answered_questions"].append(question_id)
        
        if is_correct and question_id not in self._progress["correct_questions"]:
            self._progress["correct_questions"].append(question_id)
        
        self._progress["total_time_spent"] += time_spent
        self._progress["last_active_at"] = datetime.utcnow().isoformat()
    
    def update_capability_progress(
        self,
        capability_id: str,
        completion_percentage: float,
    ) -> None:
        """更新能力模块进度"""
        self._progress["capability_progress"][capability_id] = completion_percentage
        self._progress["last_active_at"] = datetime.utcnow().isoformat()
    
    def get_stage_progress(self) -> float:
        """获取阶段完成百分比"""
        total_stages = len(self._progress["completed_stages"])
        if self._progress["current_stage"]:
            total_stages += 1
        if total_stages == 0:
            return 0.0
        return len(self._progress["completed_stages"]) / total_stages * 100
    
    def get_overall_progress(self) -> float:
        """获取总体完成百分比"""
        answered = len(self._progress["answered_questions"])
        correct = len(self._progress["correct_questions"])
        if answered == 0:
            return 0.0
        return correct / answered * 100
    
    async def save(self) -> None:
        """持久化进度数据（需要注入 Repository 实现）"""
        # TODO: 实现持久化逻辑
        pass
    
    async def load(self) -> None:
        """加载进度数据（需要注入 Repository 实现）"""
        # TODO: 实现加载逻辑
        pass

