"""
学习会话模型 (Session)

存储用户的学习会话信息，包括学习模式、进度、选中的能力模块等。
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, generate_prefixed_uuid
from .enums import LearningMode, LearningStage, SessionStatus

if TYPE_CHECKING:
    from .learning_record import LearningRecordModel
    from .note import NoteModel
    from .project import ProjectModel


class SessionModel(BaseModel):
    """
    学习会话模型
    
    跟踪用户在特定项目上的学习进度和状态。
    
    Attributes:
        id: 会话唯一标识，格式：sess_xxxxxxxxxxxx
        project_id: 关联的项目 ID
        learning_mode: 学习模式（macro/capability）
        current_stage: 当前学习阶段
        progress: 学习进度 JSON
        selected_capabilities: 选中的能力模块列表
        status: 会话状态
        summary: 会话总结（完成时生成）
    """
    
    __tablename__ = "sessions"
    __table_args__ = (
        Index("ix_sessions_project_id", "project_id"),
        Index("ix_sessions_status", "status"),
        Index("ix_sessions_learning_mode", "learning_mode"),
        Index("ix_sessions_created_at", "created_at"),
        {
            "comment": "学习会话表，跟踪用户的学习进度",
        },
    )
    
    _id_prefix = "sess"
    
    # 主键
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: generate_prefixed_uuid("sess"),
        comment="会话 ID，格式：sess_xxxxxxxxxxxx",
    )
    
    # 关联项目
    project_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联的项目 ID",
    )
    
    # 学习配置
    learning_mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=LearningMode.MACRO.value,
        comment="学习模式：macro（宏观学习）, capability（能力深挖）",
    )
    
    current_stage: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=LearningStage.OVERVIEW.value,
        comment="当前学习阶段",
    )
    
    # 进度数据 (JSONB)
    progress: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="学习进度 JSON，包含已完成的问题、正确率等",
    )
    
    selected_capabilities: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="选中的能力模块列表（能力深挖模式）",
    )
    
    # 状态管理
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=SessionStatus.ACTIVE.value,
        comment="会话状态：active, paused, completed, abandoned",
    )
    
    # 会话总结
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="会话总结（完成时生成）",
    )
    
    # 关系
    project: Mapped["ProjectModel"] = relationship(
        "ProjectModel",
        back_populates="sessions",
    )
    
    learning_records: Mapped[list["LearningRecordModel"]] = relationship(
        "LearningRecordModel",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    notes: Mapped[list["NoteModel"]] = relationship(
        "NoteModel",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return (
            f"<SessionModel(id={self.id}, project_id={self.project_id}, "
            f"mode='{self.learning_mode}', status='{self.status}')>"
        )

