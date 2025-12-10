"""
数据库模型基类（SQLAlchemy 2.0 风格）

提供统一的模型基类和公共 Mixin，包括：
- UUID 主键生成
- 时间戳字段（created_at, updated_at）
- 软删除支持（deleted_at）
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, String, event
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


def generate_prefixed_uuid(prefix: str) -> str:
    """
    生成带前缀的 UUID。
    
    Args:
        prefix: 前缀字符串，如 'proj', 'sess', 'q'
    
    Returns:
        带前缀的 UUID 字符串，格式：prefix_xxxxxxxx
    """
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""
    pass


# 元数据对象用于数据库迁移
metadata = Base.metadata


class TimestampMixin:
    """
    时间戳 Mixin
    
    为模型添加 created_at 和 updated_at 字段。
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        comment="创建时间",
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )


class SoftDeleteMixin:
    """
    软删除 Mixin
    
    为模型添加 deleted_at 字段，支持软删除。
    """
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="删除时间（软删除）",
    )
    
    @property
    def is_deleted(self) -> bool:
        """检查记录是否已软删除"""
        return self.deleted_at is not None
    
    def soft_delete(self) -> None:
        """执行软删除"""
        self.deleted_at = datetime.now(timezone.utc)
    
    def restore(self) -> None:
        """恢复软删除的记录"""
        self.deleted_at = None


class UUIDPrimaryKeyMixin:
    """
    UUID 主键 Mixin
    
    使用 UUID 作为主键，支持 PostgreSQL 原生 UUID 类型。
    """
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="主键 UUID",
    )


class PrefixedIDMixin:
    """
    带前缀 ID Mixin 基类
    
    子类需要定义 _id_prefix 类属性来指定前缀。
    例如：_id_prefix = "proj" 会生成 "proj_xxxxxxxxxxxx" 格式的 ID
    """
    
    _id_prefix: str = ""  # 子类需覆盖此属性
    
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        comment="带前缀的主键 ID",
    )
    
    @classmethod
    def generate_id(cls) -> str:
        """生成带前缀的 ID"""
        if not cls._id_prefix:
            return str(uuid.uuid4())
        return generate_prefixed_uuid(cls._id_prefix)


def set_prefixed_id(mapper, connection, target):
    """
    事件监听器：在插入前自动设置带前缀的 ID。
    """
    if hasattr(target, '_id_prefix') and target._id_prefix and not target.id:
        target.id = target.generate_id()


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """
    业务模型基类
    
    继承自 Base，并包含：
    - 时间戳字段 (created_at, updated_at)
    - 软删除字段 (deleted_at)
    
    子类需要自行定义主键。
    """
    
    __abstract__ = True
    
    def to_dict(self) -> dict[str, Any]:
        """
        将模型转换为字典。
        
        Returns:
            包含所有列值的字典
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """返回模型的字符串表示"""
        pk = getattr(self, 'id', None)
        return f"<{self.__class__.__name__}(id={pk})>"
