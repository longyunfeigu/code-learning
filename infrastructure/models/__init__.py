"""
Infrastructure models package exports.

数据库模型统一导出模块。
"""

from .base import (
    Base,
    BaseModel,
    PrefixedIDMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    generate_prefixed_uuid,
    metadata,
)
from .enums import (
    AnalysisSectionType,
    LearningMode,
    LearningStage,
    ProjectStatus,
    QuestionDifficulty,
    SessionStatus,
)

# 业务模型
from .project import ProjectModel
from .session import SessionModel
from .question import QuestionModel
from .learning_record import LearningRecordModel
from .analysis_document import AnalysisDocumentModel
from .note import NoteModel

# 原有模型
from .file_asset import FileAssetModel
from .user import UserModel

__all__ = [
    # 基类和 Mixin
    "Base",
    "BaseModel",
    "metadata",
    "TimestampMixin",
    "SoftDeleteMixin",
    "UUIDPrimaryKeyMixin",
    "PrefixedIDMixin",
    "generate_prefixed_uuid",
    # 枚举
    "ProjectStatus",
    "SessionStatus",
    "LearningMode",
    "LearningStage",
    "QuestionDifficulty",
    "AnalysisSectionType",
    # 业务模型
    "ProjectModel",
    "SessionModel",
    "QuestionModel",
    "LearningRecordModel",
    "AnalysisDocumentModel",
    "NoteModel",
    # 原有模型
    "FileAssetModel",
    "UserModel",
]
