"""
数据库模型枚举定义

定义各模型中使用的状态枚举。
"""

from enum import Enum


class ProjectStatus(str, Enum):
    """项目状态枚举"""
    
    PENDING = "pending"
    """待处理 - 项目已创建，等待分析"""
    
    CLONING = "cloning"
    """克隆中 - 正在克隆仓库"""
    
    ANALYZING = "analyzing"
    """分析中 - 正在进行项目分析"""
    
    INDEXING = "indexing"
    """索引中 - 正在建立代码索引"""
    
    READY = "ready"
    """就绪 - 项目分析完成，可以开始学习"""
    
    FAILED = "failed"
    """失败 - 项目分析失败"""


class SessionStatus(str, Enum):
    """学习会话状态枚举"""
    
    ACTIVE = "active"
    """进行中 - 会话正在进行"""
    
    PAUSED = "paused"
    """暂停 - 会话已暂停"""
    
    COMPLETED = "completed"
    """已完成 - 会话已完成"""
    
    ABANDONED = "abandoned"
    """已放弃 - 会话被用户放弃"""


class LearningMode(str, Enum):
    """学习模式枚举"""
    
    MACRO = "macro"
    """宏观学习 - 从整体了解项目架构"""
    
    CAPABILITY = "capability"
    """能力深挖 - 深入学习特定能力模块"""


class LearningStage(str, Enum):
    """学习阶段枚举"""
    
    # 宏观学习阶段
    OVERVIEW = "overview"
    """概览 - 项目整体了解"""
    
    ARCHITECTURE = "architecture"
    """架构 - 项目架构理解"""
    
    CORE_CONCEPTS = "core_concepts"
    """核心概念 - 核心组件和概念"""
    
    DATA_FLOW = "data_flow"
    """数据流 - 数据流转理解"""
    
    EXTENSION = "extension"
    """扩展 - 扩展点和定制"""
    
    # 能力深挖阶段
    CAPABILITY_INTRO = "capability_intro"
    """能力介绍 - 能力模块概述"""
    
    CAPABILITY_IMPL = "capability_impl"
    """能力实现 - 实现细节分析"""
    
    CAPABILITY_PRACTICE = "capability_practice"
    """能力实践 - 动手练习"""


class QuestionDifficulty(str, Enum):
    """问题难度枚举"""
    
    BEGINNER = "beginner"
    """入门 - 适合初学者"""
    
    INTERMEDIATE = "intermediate"
    """中级 - 需要一定基础"""
    
    ADVANCED = "advanced"
    """高级 - 需要深入理解"""
    
    EXPERT = "expert"
    """专家 - 深度探索"""


class AnalysisSectionType(str, Enum):
    """分析文档章节类型枚举（九大章节）"""
    
    EXECUTIVE_SUMMARY = "executive_summary"
    """执行摘要 - 项目概述和核心价值"""
    
    SYSTEM_ARCHITECTURE = "system_architecture"
    """系统架构 - 整体架构设计"""
    
    CORE_COMPONENTS = "core_components"
    """核心组件 - 关键组件分析"""
    
    DATA_FLOW = "data_flow"
    """数据流 - 数据流转分析"""
    
    KEY_ALGORITHMS = "key_algorithms"
    """关键算法 - 核心算法分析"""
    
    EXTENSION_POINTS = "extension_points"
    """扩展点 - 扩展和定制机制"""
    
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    """依赖分析 - 外部依赖和集成"""
    
    BEST_PRACTICES = "best_practices"
    """最佳实践 - 代码中的设计模式和实践"""
    
    LEARNING_ROADMAP = "learning_roadmap"
    """学习路线 - 推荐的学习顺序和重点"""

