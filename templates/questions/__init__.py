"""
问题模版库

按项目原型（archetype）分类：
- web_backend/: Web 后端项目
- agent_framework/: Agent 框架项目
- library/: 库/SDK 项目
- frontend_spa/: 前端 SPA 项目
- rag_system/: RAG 系统项目
- cli_tool/: CLI 工具项目
"""

from pathlib import Path
from typing import Dict, List, Any
import yaml

# 模版目录
TEMPLATES_DIR = Path(__file__).parent


def load_question_templates(archetype: str) -> List[Dict[str, Any]]:
    """
    加载指定原型的问题模版
    
    Args:
        archetype: 项目原型 (web_backend, agent_framework, etc.)
    
    Returns:
        List[Dict]: 问题模版列表
    """
    template_dir = TEMPLATES_DIR / archetype
    
    if not template_dir.exists():
        return []
    
    templates = []
    
    for yaml_file in template_dir.glob("*.yaml"):
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, list):
                templates.extend(data)
            elif isinstance(data, dict):
                templates.append(data)
    
    return templates


def get_available_archetypes() -> List[str]:
    """获取所有可用的项目原型"""
    archetypes = []
    
    for item in TEMPLATES_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            archetypes.append(item.name)
    
    return archetypes

