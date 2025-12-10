"""
子 Agent 基类定义

提供所有子 Agent 的通用功能和接口。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SubAgentResult:
    """子 Agent 执行结果"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseSubAgent(ABC):
    """
    子 Agent 基类
    
    所有子 Agent 应继承此类并实现 execute 方法。
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        tools: Optional[List[str]] = None,
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.tools = tools or []
    
    @abstractmethod
    async def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> SubAgentResult:
        """
        执行子 Agent 任务
        
        Args:
            task: 任务描述
            context: 上下文信息
        
        Returns:
            SubAgentResult 执行结果
        """
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """获取 Agent 配置"""
        return {
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "tools": self.tools,
        }

