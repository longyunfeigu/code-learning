"""
Agent 配置模块 - 智能体相关配置

定义 Agent 运行时配置，包括：
- 系统提示配置
- 工具配置
- 中间件配置
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class AgentToolConfig(BaseModel):
    """Agent 工具配置"""
    name: str
    enabled: bool = True
    description: Optional[str] = None


class AgentMiddlewareConfig(BaseModel):
    """Agent 中间件配置"""
    todo_list_enabled: bool = True
    filesystem_enabled: bool = True
    subagent_enabled: bool = True
    summarization_enabled: bool = True
    human_in_loop_enabled: bool = False


class CoachAgentConfig(BaseModel):
    """Learning Coach 主 Agent 配置"""
    
    # Agent 基本信息
    name: str = "learning-coach"
    description: str = "开源项目学习教练 - 帮助开发者深入理解开源项目"
    
    # 系统提示
    system_prompt: str = Field(
        default="""你是「开源项目学习教练」，帮助开发者深入理解开源项目。

你的能力:
1. 分析任意代码仓库的架构和设计
2. 生成个性化的学习问题序列
3. 通过苏格拉底式问答引导学习
4. 基于代码检索提供准确讲解

工作流程:
1. 用户提供仓库 URL 和学习目标
2. 委托 project-profiler 分析项目
3. 委托 repo-mapper 构建代码地图
4. 委托 question-planner 生成问题序列
5. 委托 analysis-generator 生成分析草稿
6. 进入学习循环: tutor 提问 → 用户回答 → tutor 评估 → explainer 讲解
7. 记录学习进度和笔记

重要: 使用 write_todos 规划任务，使用 task() 委托子Agent"""
    )
    
    # 中间件配置
    middleware: AgentMiddlewareConfig = Field(default_factory=AgentMiddlewareConfig)
    
    # 人工审批配置
    interrupt_on: List[str] = Field(default_factory=lambda: ["complete_learning_session"])
    
    # LLM 配置
    model: str = "gpt-4-turbo"
    temperature: float = 0.7
    max_tokens: Optional[int] = None


class SubAgentConfig(BaseModel):
    """子 Agent 基础配置"""
    name: str
    description: str
    system_prompt: str
    tools: List[str] = Field(default_factory=list)
    interrupt_on: List[str] = Field(default_factory=list)


# 预定义的子 Agent 配置
PROFILER_CONFIG = SubAgentConfig(
    name="project-profiler",
    description="分析项目结构、识别语言框架、生成项目画像",
    system_prompt="""你是项目分析专家，负责:
1. 识别项目的编程语言和框架
2. 分析目录结构和模块划分
3. 识别项目类型 (web_backend/library/agent_framework 等)
4. 输出结构化的 ProjectProfile""",
    tools=["clone_repository", "read_file", "list_directory"],
)

MAPPER_CONFIG = SubAgentConfig(
    name="repo-mapper",
    description="构建代码地图、提取符号、识别能力模块",
    system_prompt="""你是代码分析专家，负责:
1. 解析 AST 提取类、函数、方法
2. 构建模块依赖关系图
3. 识别核心类和关键方法
4. 识别能力模块候选 (插件系统、缓存层等)""",
    tools=["search_code", "parse_ast", "analyze_dependencies"],
)

PLANNER_CONFIG = SubAgentConfig(
    name="question-planner",
    description="根据项目特征生成个性化问题序列",
    system_prompt="""你是教学规划专家，负责:
1. 从问题模版库选择适用模版
2. 根据项目特征实例化问题
3. 构建问题依赖图
4. 动态调整问题序列""",
    tools=["get_question_templates", "instantiate_question"],
)

GENERATOR_CONFIG = SubAgentConfig(
    name="analysis-generator",
    description="生成九大章节的结构化分析文档",
    system_prompt="""你是技术文档专家，负责:
1. 按九大章节模版生成分析
2. 基于代码检索生成内容
3. 确保引用准确、内容有据""",
    tools=["search_code", "generate_section"],
)

TUTOR_CONFIG = SubAgentConfig(
    name="tutor",
    description="评估用户回答、提供苏格拉底式引导反馈",
    system_prompt="""你是编程导师，采用苏格拉底式教学:
1. 先让用户思考，再给予引导
2. 肯定正确部分，温和指出不足
3. 引导思考而非直接给答案
4. 推荐查看相关代码位置""",
    tools=["get_question", "evaluate_answer", "search_code"],
    interrupt_on=["generate_feedback"],
)

EXPLAINER_CONFIG = SubAgentConfig(
    name="explainer",
    description="基于 RAG 生成准确的代码讲解",
    system_prompt="""你是代码讲解专家，规则:
1. 必须引用具体的文件路径和行号
2. 不要编造不存在的代码
3. 解释设计意图，而非仅描述功能
4. 如信息不足，明确说明""",
    tools=["search_code", "get_code_snippet"],
)


# 默认 Agent 配置实例
default_coach_config = CoachAgentConfig()

