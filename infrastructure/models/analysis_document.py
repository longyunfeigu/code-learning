"""
分析文档模型 (AnalysisDocument)

存储由 Analysis Generator Agent 生成的九大章节分析文档。
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, generate_prefixed_uuid
from .enums import AnalysisSectionType

if TYPE_CHECKING:
    from .project import ProjectModel


class AnalysisDocumentModel(BaseModel):
    """
    分析文档模型
    
    存储项目的分析文档，按九大章节组织。
    
    Attributes:
        id: 文档唯一标识，格式：doc_xxxxxxxxxxxx
        project_id: 关联的项目 ID
        section_type: 章节类型（九大章节之一）
        title: 章节标题
        content: 章节内容（Markdown 格式）
        version: 文档版本号
        metadata: 额外元数据（如生成参数、引用的代码片段等）
        order_index: 章节排序索引
    """
    
    __tablename__ = "analysis_documents"
    __table_args__ = (
        Index("ix_analysis_documents_project_id", "project_id"),
        Index("ix_analysis_documents_section_type", "section_type"),
        UniqueConstraint(
            "project_id", "section_type", "version",
            name="uq_analysis_documents_project_section_version"
        ),
        {
            "comment": "分析文档表，存储项目的九大章节分析文档",
        },
    )
    
    _id_prefix = "doc"
    
    # 主键
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: generate_prefixed_uuid("doc"),
        comment="文档 ID，格式：doc_xxxxxxxxxxxx",
    )
    
    # 关联项目
    project_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联的项目 ID",
    )
    
    # 章节信息
    section_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="章节类型：executive_summary, system_architecture, core_components 等",
    )
    
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="章节标题",
    )
    
    # 内容
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        comment="章节内容（Markdown 格式）",
    )
    
    # 版本控制
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="文档版本号",
    )
    
    # 元数据 (JSONB)
    metadata_json: Mapped[Optional[dict]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        default=dict,
        comment="额外元数据，如生成参数、引用的代码片段等",
    )
    
    # 排序
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="章节排序索引",
    )
    
    # 关系
    project: Mapped["ProjectModel"] = relationship(
        "ProjectModel",
        back_populates="analysis_documents",
    )
    
    def __repr__(self) -> str:
        return (
            f"<AnalysisDocumentModel(id={self.id}, project_id={self.project_id}, "
            f"section='{self.section_type}', version={self.version})>"
        )
    
    @classmethod
    def get_section_order(cls, section_type: str) -> int:
        """获取章节的默认排序索引"""
        order_map = {
            AnalysisSectionType.EXECUTIVE_SUMMARY.value: 1,
            AnalysisSectionType.SYSTEM_ARCHITECTURE.value: 2,
            AnalysisSectionType.CORE_COMPONENTS.value: 3,
            AnalysisSectionType.DATA_FLOW.value: 4,
            AnalysisSectionType.KEY_ALGORITHMS.value: 5,
            AnalysisSectionType.EXTENSION_POINTS.value: 6,
            AnalysisSectionType.DEPENDENCY_ANALYSIS.value: 7,
            AnalysisSectionType.BEST_PRACTICES.value: 8,
            AnalysisSectionType.LEARNING_ROADMAP.value: 9,
        }
        return order_map.get(section_type, 99)

