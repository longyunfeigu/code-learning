"""
问题模型 (Question)

存储为项目生成的学习问题，包括问题内容、难度、关联文件等。
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, generate_prefixed_uuid
from .enums import LearningStage, QuestionDifficulty

if TYPE_CHECKING:
    from .learning_record import LearningRecordModel
    from .note import NoteModel
    from .project import ProjectModel


class QuestionModel(BaseModel):
    """
    问题模型
    
    存储由 Question Planner Agent 生成的学习问题。
    
    Attributes:
        id: 问题唯一标识，格式：q_xxxxxxxxxxxx
        project_id: 关联的项目 ID
        template_id: 问题模板 ID（关联 templates/questions/）
        title: 问题标题
        description: 问题详细描述
        stage: 所属学习阶段
        difficulty: 问题难度
        order_index: 在同阶段内的排序索引
        recommended_files: 推荐阅读的文件列表
        prerequisites: 前置问题 ID 列表
        hints: 提示列表
        expected_answer_points: 期望的答案要点
        tags: 标签列表
        capability_module: 关联的能力模块（能力深挖模式）
    """
    
    __tablename__ = "questions"
    __table_args__ = (
        Index("ix_questions_project_id", "project_id"),
        Index("ix_questions_stage", "stage"),
        Index("ix_questions_difficulty", "difficulty"),
        Index("ix_questions_capability_module", "capability_module"),
        Index("ix_questions_project_stage", "project_id", "stage"),
        {
            "comment": "问题表，存储为项目生成的学习问题",
        },
    )
    
    _id_prefix = "q"
    
    # 主键
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: generate_prefixed_uuid("q"),
        comment="问题 ID，格式：q_xxxxxxxxxxxx",
    )
    
    # 关联项目
    project_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联的项目 ID",
    )
    
    # 模板关联
    template_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="问题模板 ID",
    )
    
    # 问题内容
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="问题标题",
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="问题详细描述",
    )
    
    # 分类和难度
    stage: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=LearningStage.OVERVIEW.value,
        comment="所属学习阶段",
    )
    
    difficulty: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=QuestionDifficulty.INTERMEDIATE.value,
        comment="问题难度：beginner, intermediate, advanced, expert",
    )
    
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="在同阶段内的排序索引",
    )
    
    # 元数据 (JSONB)
    recommended_files: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="推荐阅读的文件路径列表",
    )
    
    prerequisites: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="前置问题 ID 列表",
    )
    
    hints: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="提示列表，逐步引导学习者",
    )
    
    expected_answer_points: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="期望的答案要点，用于评估",
    )
    
    tags: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="标签列表",
    )
    
    # 能力模块关联（能力深挖模式）
    capability_module: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="关联的能力模块",
    )
    
    # 关系
    project: Mapped["ProjectModel"] = relationship(
        "ProjectModel",
        back_populates="questions",
    )
    
    learning_records: Mapped[list["LearningRecordModel"]] = relationship(
        "LearningRecordModel",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    notes: Mapped[list["NoteModel"]] = relationship(
        "NoteModel",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return (
            f"<QuestionModel(id={self.id}, title='{self.title[:30]}...', "
            f"stage='{self.stage}', difficulty='{self.difficulty}')>"
        )

