"""
项目原型定义

定义支持的项目类型（archetype），用于问题模版选择和分析定制。
"""

from enum import Enum
from typing import Dict, List


class ProjectArchetype(str, Enum):
    """项目原型枚举"""
    
    WEB_BACKEND = "web_backend"
    """Web 后端项目 - FastAPI, Django, Flask, Express 等"""
    
    LIBRARY = "library"
    """库/SDK 项目 - 供其他项目依赖的库"""
    
    AGENT_FRAMEWORK = "agent_framework"
    """Agent 框架项目 - LangGraph, AutoGen, CrewAI 等"""
    
    RAG_SYSTEM = "rag_system"
    """RAG 系统项目 - 检索增强生成系统"""
    
    FRONTEND_SPA = "frontend_spa"
    """前端 SPA 项目 - React, Vue, Angular 等"""
    
    CLI_TOOL = "cli_tool"
    """CLI 工具项目 - 命令行工具"""
    
    MICROSERVICE = "microservice"
    """微服务项目 - 微服务架构"""
    
    DATA_PIPELINE = "data_pipeline"
    """数据管道项目 - ETL、数据处理流水线"""


# 原型识别特征
ARCHETYPE_FEATURES: Dict[ProjectArchetype, Dict[str, List[str]]] = {
    ProjectArchetype.WEB_BACKEND: {
        "frameworks": ["fastapi", "django", "flask", "express", "nestjs", "spring"],
        "directories": ["api", "routes", "controllers", "views", "middleware"],
        "files": ["app.py", "main.py", "server.py", "index.ts", "app.ts"],
    },
    ProjectArchetype.LIBRARY: {
        "frameworks": [],
        "directories": ["src", "lib", "core"],
        "files": ["setup.py", "pyproject.toml", "package.json", "Cargo.toml"],
    },
    ProjectArchetype.AGENT_FRAMEWORK: {
        "frameworks": ["langgraph", "autogen", "crewai", "langchain"],
        "directories": ["agents", "tools", "workflow", "graph", "orchestrator"],
        "files": ["agent.py", "graph.py", "workflow.py"],
    },
    ProjectArchetype.RAG_SYSTEM: {
        "frameworks": ["langchain", "llamaindex", "haystack"],
        "directories": ["retriever", "indexer", "embeddings", "vectorstore"],
        "files": ["rag.py", "retriever.py", "indexer.py"],
    },
    ProjectArchetype.FRONTEND_SPA: {
        "frameworks": ["react", "vue", "angular", "svelte", "next", "nuxt"],
        "directories": ["components", "pages", "views", "store", "hooks"],
        "files": ["App.tsx", "App.vue", "app.component.ts", "index.html"],
    },
    ProjectArchetype.CLI_TOOL: {
        "frameworks": ["click", "typer", "argparse", "commander", "yargs"],
        "directories": ["commands", "cli"],
        "files": ["cli.py", "__main__.py", "bin/"],
    },
    ProjectArchetype.MICROSERVICE: {
        "frameworks": ["grpc", "kafka", "rabbitmq"],
        "directories": ["services", "proto", "events", "messaging"],
        "files": ["docker-compose.yml", "kubernetes/", "helm/"],
    },
    ProjectArchetype.DATA_PIPELINE: {
        "frameworks": ["airflow", "prefect", "dagster", "luigi", "spark"],
        "directories": ["dags", "pipelines", "tasks", "flows"],
        "files": ["dag.py", "pipeline.py", "workflow.yaml"],
    },
}


# 原型描述
ARCHETYPE_DESCRIPTIONS: Dict[ProjectArchetype, str] = {
    ProjectArchetype.WEB_BACKEND: "Web 后端服务，处理 HTTP 请求，提供 API 接口",
    ProjectArchetype.LIBRARY: "可复用的库或 SDK，供其他项目引用",
    ProjectArchetype.AGENT_FRAMEWORK: "AI Agent 框架，支持多智能体编排和工具调用",
    ProjectArchetype.RAG_SYSTEM: "检索增强生成系统，结合搜索和生成能力",
    ProjectArchetype.FRONTEND_SPA: "前端单页应用，提供用户界面",
    ProjectArchetype.CLI_TOOL: "命令行工具，通过终端交互",
    ProjectArchetype.MICROSERVICE: "微服务架构，分布式系统组件",
    ProjectArchetype.DATA_PIPELINE: "数据处理管道，ETL 或流处理系统",
}

