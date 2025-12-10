"""
笔记模型 (Note)

存储用户在学习过程中的笔记和高亮内容。
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, generate_prefixed_uuid

if TYPE_CHECKING:
    from .question import QuestionModel
    from .session import SessionModel


class NoteModel(BaseModel):
    """
    笔记模型
    
    存储用户的学习笔记，可关联到会话或具体问题。
    
    Attributes:
        id: 笔记唯一标识，格式：note_xxxxxxxxxxxx
        session_id: 关联的会话 ID
        question_id: 关联的问题 ID（可选）
        title: 笔记标题
        content: 笔记内容（Markdown 格式）
        highlights: 高亮内容列表 JSON
        tags: 标签列表
        source_file: 关联的源文件路径（可选）
        source_lines: 关联的代码行范围（可选）
    """
    
    __tablename__ = "notes"
    __table_args__ = (
        Index("ix_notes_session_id", "session_id"),
        Index("ix_notes_question_id", "question_id"),
        Index("ix_notes_created_at", "created_at"),
        {
            "comment": "笔记表，存储用户的学习笔记",
        },
    )
    
    _id_prefix = "note"
    
    # 主键
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: generate_prefixed_uuid("note"),
        comment="笔记 ID，格式：note_xxxxxxxxxxxx",
    )
    
    # 关联会话（必需）
    session_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联的会话 ID",
    )
    
    # 关联问题（可选）
    question_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        ForeignKey("questions.id", ondelete="SET NULL"),
        nullable=True,
        comment="关联的问题 ID（可选）",
    )
    
    # 笔记内容
    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="笔记标题",
    )
    
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        comment="笔记内容（Markdown 格式）",
    )
    
    # 高亮内容 (JSONB)
    highlights: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="高亮内容列表，包含选中文本和位置信息",
    )
    
    # 标签
    tags: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="标签列表",
    )
    
    # 关联源代码
    source_file: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="关联的源文件路径",
    )
    
    source_lines: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="关联的代码行范围，如 {start: 10, end: 20}",
    )
    
    # 关系
    session: Mapped["SessionModel"] = relationship(
        "SessionModel",
        back_populates="notes",
    )
    
    question: Mapped[Optional["QuestionModel"]] = relationship(
        "QuestionModel",
        back_populates="notes",
    )
    
    def __repr__(self) -> str:
        title_preview = self.title[:20] if self.title else "Untitled"
        return f"<NoteModel(id={self.id}, title='{title_preview}...')>"

