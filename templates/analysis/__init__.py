"""
分析文档模版

包含九大章节的分析模版：
1. 整体架构分析
2. 各模块职责与内部关系
3. 核心类解剖
4. 关键方法深度解析
5. 模块间调用依赖关系分析
6. 核心流程分析
7. 核心入口 & 主要数据流
8. 设计亮点与精妙之处
9. 从源码看最佳实践
"""

from pathlib import Path
from typing import Dict, Optional

TEMPLATES_DIR = Path(__file__).parent


# 章节定义
ANALYSIS_SECTIONS = {
    "1_architecture": {
        "id": "1_architecture",
        "title": "整体架构分析",
        "description": "分析项目的整体架构风格、设计原则和分层结构",
        "template_file": "1_architecture.md",
    },
    "2_modules": {
        "id": "2_modules",
        "title": "各模块职责与内部关系",
        "description": "详细说明各模块的职责划分和协作方式",
        "template_file": "2_modules.md",
    },
    "3_core_classes": {
        "id": "3_core_classes",
        "title": "核心类解剖",
        "description": "深入分析核心类的设计和实现",
        "template_file": "3_core_classes.md",
    },
    "4_key_methods": {
        "id": "4_key_methods",
        "title": "关键方法深度解析",
        "description": "解析关键方法的算法逻辑和实现细节",
        "template_file": "4_key_methods.md",
    },
    "5_dependencies": {
        "id": "5_dependencies",
        "title": "模块间调用依赖关系分析",
        "description": "分析模块间的依赖关系和调用链",
        "template_file": "5_dependencies.md",
    },
    "6_core_flows": {
        "id": "6_core_flows",
        "title": "核心流程分析",
        "description": "追踪核心业务流程的实现",
        "template_file": "6_core_flows.md",
    },
    "7_entry_dataflow": {
        "id": "7_entry_dataflow",
        "title": "核心入口 & 主要数据流",
        "description": "分析项目入口和数据流转路径",
        "template_file": "7_entry_dataflow.md",
    },
    "8_highlights": {
        "id": "8_highlights",
        "title": "设计亮点与精妙之处",
        "description": "发现和总结项目的设计亮点",
        "template_file": "8_highlights.md",
    },
    "9_best_practices": {
        "id": "9_best_practices",
        "title": "从源码看最佳实践",
        "description": "从源码中提炼可借鉴的最佳实践",
        "template_file": "9_best_practices.md",
    },
}


def get_section_template(section_id: str) -> Optional[str]:
    """
    获取章节模版内容
    
    Args:
        section_id: 章节 ID
    
    Returns:
        str: 模版内容，不存在则返回 None
    """
    if section_id not in ANALYSIS_SECTIONS:
        return None
    
    template_file = TEMPLATES_DIR / ANALYSIS_SECTIONS[section_id]["template_file"]
    
    if not template_file.exists():
        return None
    
    return template_file.read_text(encoding="utf-8")


def get_all_sections() -> Dict:
    """获取所有章节定义"""
    return ANALYSIS_SECTIONS.copy()

