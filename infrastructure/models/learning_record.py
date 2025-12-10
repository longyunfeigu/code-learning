"""
学习记录模型 (LearningRecord)

存储用户对问题的回答、评估结果和讲解内容。
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, generate_prefixed_uuid

if TYPE_CHECKING:
    from .question import QuestionModel
    from .session import SessionModel


class LearningRecordModel(BaseModel):
    """
    学习记录模型
    
    记录用户在学习会话中对问题的回答和评估结果。
    
    Attributes:
        id: 记录唯一标识，格式：lr_xxxxxxxxxxxx
        session_id: 关联的会话 ID
        question_id: 关联的问题 ID
        answer: 用户的回答内容
        evaluation: 评估结果 JSON（由 Tutor Agent 生成）
        score: 得分（0-100）
        explanation: 讲解内容 JSON（由 Explainer Agent 生成）
        time_spent: 用时（秒）
        attempt_number: 尝试次数
        hints_used: 使用的提示数量
        is_correct: 是否回答正确
        feedback: Tutor 的反馈
    """
    
    __tablename__ = "learning_records"
    __table_args__ = (
        Index("ix_learning_records_session_id", "session_id"),
        Index("ix_learning_records_question_id", "question_id"),
        Index("ix_learning_records_session_question", "session_id", "question_id"),
        Index("ix_learning_records_created_at", "created_at"),
        {
            "comment": "学习记录表，存储用户的回答和评估结果",
        },
    )
    
    _id_prefix = "lr"
    
    # 主键
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: generate_prefixed_uuid("lr"),
        comment="学习记录 ID，格式：lr_xxxxxxxxxxxx",
    )
    
    # 关联会话和问题
    session_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联的会话 ID",
    )
    
    question_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联的问题 ID",
    )
    
    # 回答内容
    answer: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="用户的回答内容",
    )
    
    # 评估结果 (JSONB)
    evaluation: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="评估结果 JSON，包含各要点的匹配情况",
    )
    
    score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="得分（0-100）",
    )
    
    is_correct: Mapped[Optional[bool]] = mapped_column(
        nullable=True,
        default=None,
        comment="是否回答正确",
    )
    
    # 讲解内容 (JSONB)
    explanation: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="讲解内容 JSON（由 Explainer Agent 生成）",
    )
    
    # Tutor 反馈
    feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Tutor 的反馈和引导",
    )
    
    # 学习统计
    time_spent: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="用时（秒）",
    )
    
    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="尝试次数",
    )
    
    hints_used: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="使用的提示数量",
    )
    
    # 关系
    session: Mapped["SessionModel"] = relationship(
        "SessionModel",
        back_populates="learning_records",
    )
    
    question: Mapped["QuestionModel"] = relationship(
        "QuestionModel",
        back_populates="learning_records",
    )
    
    def __repr__(self) -> str:
        return (
            f"<LearningRecordModel(id={self.id}, session_id={self.session_id}, "
            f"question_id={self.question_id}, score={self.score})>"
        )

