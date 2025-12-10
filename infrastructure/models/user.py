"""
用户模型占位（User）

当前为无用户概念的单租户场景，此模型为占位模型。
后续实现多租户时可扩展。
"""

from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .file_asset import FileAssetModel


class UserModel(BaseModel):
    """
    用户模型（占位）
    
    当前版本为单租户场景，此模型作为占位使用。
    后续可扩展为完整的用户系统。
    
    Attributes:
        id: 用户 ID
        email: 邮箱（唯一）
        name: 用户名
    """
    
    __tablename__ = "users"
    __table_args__ = {
        "comment": "用户表（当前为占位，单租户场景）",
    }
    
    # 主键（使用整数，与 file_asset 的外键兼容）
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="用户 ID",
    )
    
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        comment="用户邮箱",
    )
    
    name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="用户名",
    )
    
    # 关系
    file_assets: Mapped[List["FileAssetModel"]] = relationship(
        "FileAssetModel",
        back_populates="owner",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email='{self.email}')>"
