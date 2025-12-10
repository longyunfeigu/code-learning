"""
项目模型 (Project)

存储待学习的代码仓库信息，包括元数据、分析结果等。
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Index, String, Text, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, generate_prefixed_uuid
from .enums import ProjectStatus

if TYPE_CHECKING:
    from .analysis_document import AnalysisDocumentModel
    from .question import QuestionModel
    from .session import SessionModel


class ProjectModel(BaseModel):
    """
    项目模型
    
    存储代码仓库的基本信息、分析元数据和处理状态。
    
    Attributes:
        id: 项目唯一标识，格式：proj_xxxxxxxxxxxx
        repo_url: Git 仓库地址
        name: 项目名称（从仓库 URL 或用户输入获取）
        description: 项目描述
        archetype: 项目原型（web_backend, library, agent_framework 等）
        primary_language: 主要编程语言
        framework: 使用的主要框架
        profile: 项目画像 JSON（由 Profiler Agent 生成）
        repo_map: 仓库结构映射 JSON（由 Mapper Agent 生成）
        capabilities: 识别出的能力模块列表
        status: 项目处理状态
        error_message: 如果处理失败，记录错误信息
        local_path: 本地克隆路径
    """
    
    __tablename__ = "projects"
    __table_args__ = (
        Index("ix_projects_status", "status"),
        Index("ix_projects_archetype", "archetype"),
        Index("ix_projects_created_at", "created_at"),
        {
            "comment": "项目表，存储待学习的代码仓库信息",
        },
    )
    
    _id_prefix = "proj"
    
    # 主键
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: generate_prefixed_uuid("proj"),
        comment="项目 ID，格式：proj_xxxxxxxxxxxx",
    )
    
    # 基本信息
    repo_url: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        comment="Git 仓库地址",
    )
    
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="项目名称",
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="项目描述",
    )
    
    # 项目元数据
    archetype: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="项目原型：web_backend, library, agent_framework 等",
    )
    
    primary_language: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="主要编程语言",
    )
    
    framework: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="使用的主要框架",
    )
    
    # 分析数据 (JSONB)
    profile: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="项目画像 JSON（由 Profiler Agent 生成）",
    )
    
    repo_map: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="仓库结构映射 JSON（由 Mapper Agent 生成）",
    )
    
    capabilities: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="识别出的能力模块列表",
    )
    
    # 状态管理
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ProjectStatus.PENDING.value,
        comment="项目状态：pending, cloning, analyzing, indexing, ready, failed",
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="错误信息（如果处理失败）",
    )
    
    # 本地存储路径
    local_path: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="本地克隆路径",
    )
    
    # 关系
    sessions: Mapped[list["SessionModel"]] = relationship(
        "SessionModel",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    questions: Mapped[list["QuestionModel"]] = relationship(
        "QuestionModel",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    analysis_documents: Mapped[list["AnalysisDocumentModel"]] = relationship(
        "AnalysisDocumentModel",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<ProjectModel(id={self.id}, name='{self.name}', status='{self.status}')>"

