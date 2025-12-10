# 开源项目学习教练 AI 智能体 - 技术架构文档

> **版本**: v1.0  
> **更新日期**: 2025-12-10  
> **文档状态**: 草稿  
> **作者**: AI Architecture Team

---

## 目录

1. [架构概述](#1-架构概述)
   - 1.1 架构设计原则
   - 1.2 架构风格
   - 1.3 架构全景图
2. [系统分层架构](#2-系统分层架构)
   - 2.1 分层架构图 (DDD 风格)
   - 2.2 各层职责说明
   - 2.3 目录结构
3. [组件部署架构](#3-组件部署架构)
   - 3.1 部署架构图
   - 3.2 服务清单
   - 3.3 网络架构
   - 3.4 端口规划
4. [核心通信流程](#4-核心通信流程)
   - 4.1 项目初始化流程
   - 4.2 学习会话流程
   - 4.3 问题驱动学习流程
   - 4.4 异常处理流程
5. [数据流向详解](#5-数据流向详解)
   - 5.1 项目分析数据流
   - 5.2 配置数据流转
   - 5.3 完整数据流图
6. [关键组件详解](#6-关键组件详解)
   - 6.1 Project Profiler（项目画像器）
   - 6.2 Repo Mapper（代码地图生成器）
   - 6.3 Question Planner（问题规划器）
   - 6.4 Analysis Generator（分析文档生成器）
   - 6.5 Tutor Agent（学习教练智能体）
   - 6.6 Explainer Agent（代码讲解智能体）
   - 6.7 Note & Progress Manager（笔记与进度管理）
7. [技术选型说明](#7-技术选型说明)
   - 7.1 关键设计模式
   - 7.2 核心通信协议
   - 7.3 技术栈对比
8. [扩展与优化建议](#8-扩展与优化建议)
   - 8.1 性能优化
   - 8.2 可靠性设计
   - 8.3 可观测性
   - 8.4 扩展性设计
9. [附录](#附录)
   - A. 部署依赖关系
   - B. 环境变量清单
   - C. 数据模型设计
   - D. 参考资料

---

## 1. 架构概述

### 1.1 产品概述

> 一个面向开发者的「**开源项目学习教练 AI 智能体**」，能基于任意代码仓库，结合用户的学习目标，用**问题驱动 + 架构分析 + 代码讲解 + 能力模块深挖**的方式，让开发者在有限时间内真正吃透一个项目。

#### 核心价值

| 价值点 | 描述 |
|--------|------|
| **学习路线化** | 从"代码海洋"变成清晰的学习阶段（整体架构 → 模块 → 核心类/方法 → 设计亮点） |
| **能力模块深挖** | 支持只学习特定能力模块（Agent Harness、插件系统、缓存层、错误处理等） |
| **结构化输出** | 自动生成结构化的项目分析文档（整体架构、模块职责、核心类、关键流程、最佳实践） |
| **能力提升** | 通过苏格拉底式问答（Socratic Tutor），让用户自我解释后再纠偏 |

### 1.2 架构设计原则

| 原则 | 说明 | 实践方式 |
|------|------|----------|
| **模块化** | 各智能体独立运行，职责清晰 | DeepAgents SubAgent 架构，每个 Agent 独立上下文 |
| **可扩展** | 支持新增项目类型、问题模版、能力模块 | 模版库 + 中间件插件化设计 |
| **松耦合** | Agent 间通过中间件通信 | DeepAgents SubAgentMiddleware + 任务委托 |
| **数据驱动** | 基于代码索引和检索生成内容 | RAG + 向量索引 + 结构化搜索 |
| **上下文隔离** | 子 Agent 隔离上下文，防止污染 | SubAgentMiddleware 上下文隔离 |
| **长期记忆** | 支持任务规划和进度持久化 | FilesystemMiddleware + TodoListMiddleware |
| **可观测** | 全链路追踪、日志、指标 | structlog + OpenTelemetry + LangSmith |
| **用户中心** | 个性化学习路径、进度持久化 | 用户画像 + 学习档案 |

### 1.3 架构风格

| 维度 | 选型 |
|------|------|
| **整体架构风格** | 模块化单体 + 多智能体编排（Multi-Agent Orchestration） |
| **智能体框架** | DeepAgents（基于 LangGraph，内置中间件架构） |
| **核心中间件** | TodoListMiddleware（任务规划）+ FilesystemMiddleware（长期记忆）+ SubAgentMiddleware（子Agent编排） |
| **通信模式** | 同步 REST API（前端交互）+ 异步中间件（Agent 内部）+ WebSocket（实时对话） |
| **数据架构** | 混合架构：关系型（PostgreSQL）+ 向量数据库（Qdrant/ChromaDB）+ 缓存（Redis） |

### 1.4 DeepAgents 中间件架构

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DeepAgents 中间件栈                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐           │
│  │ TodoListMiddleware │  │FilesystemMiddleware│  │ SubAgentMiddleware │           │
│  │                    │  │                    │  │                    │           │
│  │ • write_todos      │  │ • ls               │  │ • task(agent_name) │           │
│  │ • mark_complete    │  │ • read_file        │  │ • 上下文隔离       │           │
│  │ • 任务进度跟踪     │  │ • write_file       │  │ • 结果聚合         │           │
│  │                    │  │ • edit_file        │  │                    │           │
│  │ 用于：Question     │  │ 用于：笔记存储     │  │ 用于：Profiler     │           │
│  │      Planner       │  │       进度持久化   │  │       Mapper       │           │
│  │                    │  │       分析文档     │  │       Tutor        │           │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘           │
│                                                                                  │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐           │
│  │SummarizationMW    │  │HumanInTheLoopMW   │  │PromptCachingMW    │           │
│  │                    │  │                    │  │                    │           │
│  │ • 超170k自动摘要  │  │ • 敏感操作审批    │  │ • 系统提示缓存    │           │
│  │ • 防止上下文溢出  │  │ • 学习进度确认    │  │ • 降低 API 成本   │           │
│  │                    │  │                    │  │                    │           │
│  │ 用于：大仓库分析  │  │ 用于：苏格拉底    │  │ 用于：重复问答    │           │
│  │                    │  │       式教学      │  │                    │           │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘           │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │   LangGraph Runtime │
                            │   (底层状态图引擎)   │
                            └─────────────────────┘
```

### 1.5 架构全景图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              用户接入层 (Presentation)                           │
│   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐                    │
│   │   Web 前端    │   │ VS Code 插件  │   │     CLI       │                    │
│   │  (React/Vue)  │   │ (Extension)   │   │   (Typer)     │                    │
│   └───────┬───────┘   └───────┬───────┘   └───────┬───────┘                    │
└───────────┼───────────────────┼───────────────────┼─────────────────────────────┘
            │                   │                   │
            └───────────────────┼───────────────────┘
                                │ HTTP/WebSocket
                                ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            网关/负载均衡层                                        │
│                     Nginx / Traefik (反向代理 + SSL 终止)                        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         业务服务层 (FastAPI Backend)                             │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                     Code Learning Coach Service                          │   │
│   │  ┌──────────────────────────────────────────────────────────────────┐   │   │
│   │  │              智能体编排层 (DeepAgents + Middleware Stack)          │   │   │
│   │  │  ┌─────────────────────────────────────────────────────────────┐ │   │   │
│   │  │  │  Main Agent (Learning Coach)                                │ │   │   │
│   │  │  │  ├─ TodoListMiddleware (任务规划)                           │ │   │   │
│   │  │  │  ├─ FilesystemMiddleware (笔记/进度存储)                    │ │   │   │
│   │  │  │  ├─ SubAgentMiddleware (子Agent调度)                        │ │   │   │
│   │  │  │  └─ SummarizationMiddleware (上下文摘要)                    │ │   │   │
│   │  │  └─────────────────────────────────────────────────────────────┘ │   │   │
│   │  │  ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐   │   │   │
│   │  │  │Project  │ Repo    │Question │Analysis │ Tutor   │Explainer│   │   │   │
│   │  │  │Profiler │ Mapper  │Planner  │Generator│SubAgent │SubAgent │   │   │   │
│   │  │  │SubAgent │SubAgent │SubAgent │SubAgent │         │         │   │   │   │
│   │  │  └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘   │   │   │
│   │  └──────────────────────────────────────────────────────────────────┘   │   │
│   │  ┌────────────┬────────────┬────────────┬────────────┬────────────┐     │   │
│   │  │ Auth 模块  │ Session 管理│ 进度管理   │ 笔记管理   │ Webhook    │     │   │
│   │  └────────────┴────────────┴────────────┴────────────┴────────────┘     │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            工具 & 数据层                                         │
│   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐                    │
│   │  LLM 服务     │   │  代码索引服务  │   │  Git 服务     │                    │
│   │  - OpenAI     │   │  - tree-sitter │   │  - 仓库克隆   │                    │
│   │  - Claude     │   │  - 向量化      │   │  - 版本管理   │                    │
│   │  - 本地模型   │   │  - 符号搜索    │   │  - Diff 分析  │                    │
│   └───────────────┘   └───────────────┘   └───────────────┘                    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            数据存储层                                            │
│   ┌───────────────────────────────┐   ┌───────────────────────────────┐        │
│   │         PostgreSQL            │   │       Qdrant / ChromaDB       │        │
│   │  - 用户数据                   │   │  - 代码向量索引               │        │
│   │  - 项目元数据                 │   │  - 文档向量索引               │        │
│   │  - 学习进度                   │   │  - 语义搜索                   │        │
│   │  - 问题模版                   │   │                               │        │
│   │  - 分析文档                   │   │                               │        │
│   └───────────────────────────────┘   └───────────────────────────────┘        │
│   ┌───────────────────────────────┐   ┌───────────────────────────────┐        │
│   │           Redis               │   │     对象存储 (MinIO/S3)       │        │
│   │  - 会话缓存                   │   │  - 仓库文件                   │        │
│   │  - LLM 响应缓存               │   │  - 生成文档                   │        │
│   │  - 任务队列                   │   │  - 用户笔记                   │        │
│   └───────────────────────────────┘   └───────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 系统分层架构

### 2.1 分层架构图 (DDD 风格 + DeepAgents)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          API 层 (Presentation)                               │
│  ┌────────────────┬──────────────┬─────────────┬──────────────┬──────────┐  │
│  │ /projects      │ /sessions    │ /questions  │ /analysis    │ /notes   │  │
│  │ (项目管理)     │ (学习会话)   │ (问题系统)  │ (分析文档)   │ (笔记)   │  │
│  ├────────────────┴──────────────┴─────────────┴──────────────┴──────────┤  │
│  │ /agents/chat   │ WebSocket 实时对话接口                                │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│                        应用层 (Application)                                  │
│  ┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐  │
│  │ ProjectService  │ SessionService  │ LearningService │ AnalysisService │  │
│  │ (项目生命周期)  │ (会话编排)      │ (学习流程)      │ (文档生成)      │  │
│  ├─────────────────┴─────────────────┴─────────────────┴─────────────────┤  │
│  │              DeepAgents Coach (Main Agent + Middleware)                │  │
│  │  ┌───────────────────────────────────────────────────────────────┐    │  │
│  │  │ Middleware Stack:                                              │    │  │
│  │  │   TodoListMiddleware │ FilesystemMiddleware │ SubAgentMiddleware│   │  │
│  │  ├───────────────────────────────────────────────────────────────┤    │  │
│  │  │ SubAgents (via SubAgentMiddleware):                            │    │  │
│  │  │  ┌─────────┬─────────┬─────────┬─────────┬─────────┐          │    │  │
│  │  │  │Profiler │ Mapper  │ Planner │Generator│ Tutor   │          │    │  │
│  │  │  │SubAgent │SubAgent │SubAgent │SubAgent │SubAgent │          │    │  │
│  │  │  └─────────┴─────────┴─────────┴─────────┴─────────┘          │    │  │
│  │  └───────────────────────────────────────────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│                        领域层 (Domain)                                       │
│  Entity: Project, LearningSession, Question, Analysis, Note, UserProgress   │
│  Value Object: ProjectProfile, RepoMap, QuestionGraph, CapabilityModule     │
│  Domain Service: CodeAnalyzer, QuestionGenerator, ProgressTracker           │
│  Domain Event: ProjectAnalyzed, QuestionAnswered, AnalysisGenerated         │
│  Repository Interfaces: IProjectRepo, ISessionRepo, IQuestionRepo           │
├─────────────────────────────────────────────────────────────────────────────┤
│                     基础设施层 (Infrastructure)                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ LangChain 封装层  │  Repository Impl    │  External Services           │ │
│  │  - ChatModels     │  - PostgresRepo     │  - GitService                │ │
│  │  - Embeddings     │  - RedisCache       │  - TreeSitterParser          │ │
│  │  - VectorStores   │  - UnitOfWork       │  - CodeIndexer               │ │
│  │  - Retrievers     │                     │                              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 各层职责说明

| 层级 | 职责 | 包含内容 | 依赖规则 |
|------|------|----------|----------|
| **API 层** | HTTP 请求处理、WebSocket 连接、参数校验、响应格式化 | Routes, Middleware, Schemas | 只能调用应用层 |
| **应用层** | 用例编排、Agent 协调、事务管理、DTO 转换 | Services, AgentOrchestrator, DTOs | 只能调用领域层 |
| **领域层** | 核心业务逻辑：项目分析、问题生成、学习流程 | Entities, Value Objects, Domain Services | 不依赖任何层 |
| **基础设施层** | LangChain 封装 (LLM/Embedding/VectorStore)、数据持久化、代码索引 | LangChain 组件, Repositories, Adapters | 实现领域层接口 |

### 2.3 目录结构

```
code-learning-coach/
├── api/                              # API 层
│   ├── routes/                       # 路由定义
│   │   ├── projects.py               # 项目管理接口
│   │   ├── sessions.py               # 学习会话接口
│   │   ├── questions.py              # 问题系统接口
│   │   ├── analysis.py               # 分析文档接口
│   │   ├── notes.py                  # 笔记管理接口
│   │   └── agents.py                 # Agent 对话接口 (WebSocket)
│   ├── middleware/                   # 中间件
│   │   ├── auth.py                   # 认证
│   │   ├── logging.py                # 请求日志
│   │   ├── rate_limit.py             # 限流
│   │   └── error_handler.py          # 全局异常处理
│   └── schemas/                      # 请求/响应模型
│       ├── requests/
│       └── responses/
│
├── application/                      # 应用层
│   ├── services/                     # 应用服务
│   │   ├── project_service.py        # 项目服务
│   │   ├── session_service.py        # 会话服务
│   │   ├── learning_service.py       # 学习流程服务
│   │   └── analysis_service.py       # 分析服务
│   ├── agents/                       # DeepAgents 编排
│   │   ├── coach_agent.py            # 主 Agent (Learning Coach)
│   │   ├── config.py                 # Agent 配置
│   │   ├── middleware/               # 自定义中间件
│   │   │   ├── progress_middleware.py    # 进度跟踪中间件
│   │   │   └── rag_middleware.py         # RAG 检索中间件
│   │   └── subagents/                # 子 Agent 定义
│   │       ├── profiler_agent.py     # 项目画像子Agent
│   │       ├── mapper_agent.py       # 代码地图子Agent
│   │       ├── planner_agent.py      # 问题规划子Agent
│   │       ├── generator_agent.py    # 分析生成子Agent
│   │       ├── tutor_agent.py        # 学习教练子Agent
│   │       └── explainer_agent.py    # 代码讲解子Agent
│   └── dtos/                         # 数据传输对象
│       ├── project_dto.py
│       ├── session_dto.py
│       └── question_dto.py
│
├── domain/                           # 领域层
│   ├── entities/                     # 实体
│   │   ├── project.py                # 项目实体
│   │   ├── learning_session.py       # 学习会话
│   │   ├── question.py               # 问题
│   │   ├── analysis.py               # 分析文档
│   │   └── note.py                   # 笔记
│   ├── value_objects/                # 值对象
│   │   ├── project_profile.py        # 项目画像
│   │   ├── repo_map.py               # 代码地图
│   │   ├── question_graph.py         # 问题图
│   │   └── capability_module.py      # 能力模块
│   ├── services/                     # 领域服务
│   │   ├── code_analyzer.py          # 代码分析
│   │   ├── question_generator.py     # 问题生成
│   │   └── progress_tracker.py       # 进度跟踪
│   ├── events/                       # 领域事件
│   │   ├── project_events.py
│   │   └── learning_events.py
│   └── repositories/                 # 仓储接口
│       ├── project_repository.py
│       ├── session_repository.py
│       └── question_repository.py
│
├── infrastructure/                   # 基础设施层
│   ├── persistence/                  # 持久化
│   │   ├── models/                   # ORM 模型
│   │   │   ├── project_model.py
│   │   │   ├── session_model.py
│   │   │   └── question_model.py
│   │   ├── repositories/             # 仓储实现
│   │   │   ├── postgres_project_repo.py
│   │   │   └── postgres_session_repo.py
│   │   └── database.py               # 数据库连接
│   ├── langchain/                    # LangChain 封装层
│   │   ├── llm.py                    # LLM 配置 (ChatOpenAI, ChatAnthropic, ChatOllama)
│   │   ├── embeddings.py             # Embedding 配置 (OpenAI, HuggingFace)
│   │   ├── vectorstore.py            # 向量库配置 (Qdrant, Chroma, PGVector)
│   │   ├── retrievers.py             # Retriever 配置 (多向量检索、上下文压缩)
│   │   ├── prompts/                  # Prompt 模版
│   │   │   ├── code_explain.py       # 代码讲解模版
│   │   │   ├── question_generate.py  # 问题生成模版
│   │   │   └── tutor.py              # 教学对话模版
│   │   └── chains/                   # LangChain Chains
│   │       ├── rag_chain.py          # RAG 检索链
│   │       └── qa_chain.py           # 问答链
│   ├── code_analysis/                # 代码分析服务
│   │   ├── git_service.py            # Git 操作
│   │   ├── tree_sitter_parser.py     # AST 解析
│   │   ├── code_indexer.py           # 代码索引
│   │   └── symbol_search.py          # 符号搜索
│   ├── cache/                        # 缓存实现
│   │   └── redis_cache.py
│   └── external/                     # 外部服务
│       └── webhook_client.py
│
├── core/                             # 核心配置
│   ├── config.py                     # 配置管理
│   ├── exceptions.py                 # 异常定义
│   ├── logging_config.py             # 日志配置
│   └── responses.py                  # 响应格式
│
├── shared/                           # 共享工具
│   ├── utils/
│   │   ├── text_utils.py
│   │   └── code_utils.py
│   └── constants/
│       ├── archetype.py              # 项目原型定义
│       └── capability.py             # 能力模块定义
│
├── templates/                        # 模版库
│   ├── questions/                    # 问题模版
│   │   ├── web_backend/
│   │   ├── agent_framework/
│   │   ├── library/
│   │   └── frontend_spa/
│   └── analysis/                     # 分析模版
│       └── nine_sections.md          # 九大章节模版
│
├── tests/                            # 测试
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── alembic/                          # 数据库迁移
│   ├── versions/
│   └── alembic.ini
│
├── main.py                           # 应用入口
├── requirements.txt                  # 依赖
└── docker-compose.yml                # 容器编排
```

---

## 3. 组件部署架构

### 3.1 部署架构图

```
                                    用户端 (Web/VS Code/CLI)
                                         │
                                         │ HTTPS / WSS
                                         ▼
                              ┌──────────────────────┐
                              │   Nginx / Traefik    │
                              │   (反向代理 + SSL)   │
                              └──────────┬───────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│   Backend Instance #1 │  │   Backend Instance #2 │  │   Backend Instance #N │
│   (Port: 8000)        │  │   (Port: 8000)        │  │   (Port: 8000)        │
│   ┌─────────────────┐ │  │   ┌─────────────────┐ │  │   ┌─────────────────┐ │
│   │ FastAPI App     │ │  │   │ FastAPI App     │ │  │   │ FastAPI App     │ │
│   │ + LangGraph     │ │  │   │ + LangGraph     │ │  │   │ + LangGraph     │ │
│   │ + Agent Runtime │ │  │   │ + Agent Runtime │ │  │   │ + Agent Runtime │ │
│   └─────────────────┘ │  │   └─────────────────┘ │  │   └─────────────────┘ │
└───────────┬───────────┘  └───────────┬───────────┘  └───────────┬───────────┘
            │                          │                          │
            └────────────────┬─────────┴──────────────────────────┘
                             │
              ┌──────────────┼──────────────┬──────────────┐
              │              │              │              │
              ▼              ▼              ▼              ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│   PostgreSQL    │  │    Redis     │  │   Qdrant     │  │   MinIO / S3     │
│   (主从复制)    │  │  (Cluster)   │  │  (Vector DB) │  │   (对象存储)     │
│   Port: 5432    │  │  Port: 6379  │  │  Port: 6333  │  │   Port: 9000     │
└─────────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Celery Worker Pool                                 │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│   │  Worker #1      │  │  Worker #2      │  │  Worker #N      │             │
│   │  (代码索引)     │  │  (文档生成)     │  │  (异步分析)     │             │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 服务清单

#### 3.2.1 必须部署的服务

| 服务名称 | 说明 | 默认端口 | 资源需求 | 扩展策略 |
|----------|------|----------|----------|----------|
| Backend API | FastAPI + LangGraph 主服务 | 8000 | 2 CPU, 4GB RAM | 水平扩展 |
| PostgreSQL | 主数据库（用户、项目、进度） | 5432 | 2 CPU, 4GB RAM | 主从复制 |
| Redis | 缓存、会话、任务队列 | 6379 | 1 CPU, 2GB RAM | 集群模式 |
| Qdrant | 向量数据库（代码语义搜索） | 6333 | 2 CPU, 4GB RAM | 分片扩展 |
| Celery Worker | 异步任务（代码索引、文档生成） | - | 2 CPU, 4GB RAM | 水平扩展 |
| MinIO | 对象存储（仓库文件、文档） | 9000 | 1 CPU, 2GB RAM | 分布式部署 |

#### 3.2.2 可选部署的服务

| 服务名称 | 说明 | 适用场景 |
|----------|------|----------|
| Nginx / Traefik | 反向代理、负载均衡 | 生产环境 |
| Prometheus + Grafana | 监控可视化 | 需要详细性能监控 |
| ELK Stack | 日志聚合分析 | 需要日志分析 |
| Ollama | 本地 LLM 推理 | 离线部署、隐私敏感场景 |

### 3.3 网络架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         公网 (Internet)                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTPS (443)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DMZ 区域                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Nginx / Traefik                        │   │
│  │                   (SSL 终止, 反向代理, 限流)              │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP (内网)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        应用区域                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Backend     │  │  Celery      │  │  Flower      │          │
│  │  容器集群    │  │  Worker 池   │  │  (任务监控)  │          │
│  │  (FastAPI)   │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ TCP (内网)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据区域                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  PostgreSQL  │  │    Redis     │  │   Qdrant     │          │
│  │  (主从)      │  │  (Cluster)   │  │  (向量存储)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐                                              │
│  │    MinIO     │                                              │
│  │  (对象存储)  │                                              │
│  └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
```

### 3.4 端口规划

| 服务 | 端口 | 协议 | 暴露范围 | 说明 |
|------|------|------|----------|------|
| Nginx | 80, 443 | HTTP/HTTPS | 公网 | 入口网关 |
| Backend API | 8000 | HTTP/WS | 内网 | 业务接口 + WebSocket |
| PostgreSQL | 5432 | TCP | 数据区 | 主数据库 |
| Redis | 6379 | TCP | 应用区 | 缓存 + 队列 |
| Qdrant | 6333 | HTTP | 数据区 | 向量搜索 API |
| MinIO | 9000 | HTTP | 数据区 | 对象存储 API |
| Flower | 5555 | HTTP | 内网 | Celery 监控 |

---

## 4. 核心通信流程

### 4.1 项目初始化流程

#### 时序图

```
用户                 Frontend              Backend                Celery Worker         Git/Storage
  │                    │                      │                       │                    │
  │  1. 提交仓库URL    │                      │                       │                    │
  │ ─────────────────► │                      │                       │                    │
  │                    │  2. POST /projects   │                       │                    │
  │                    │ ────────────────────►│                       │                    │
  │                    │                      │                       │                    │
  │                    │                      │  3. 创建异步任务       │                    │
  │                    │                      │ ─────────────────────►│                    │
  │                    │                      │                       │                    │
  │                    │  4. 返回 project_id  │                       │                    │
  │                    │ ◄────────────────────│                       │                    │
  │                    │                      │                       │                    │
  │  5. 显示处理中     │                      │                       │  6. 克隆仓库       │
  │ ◄───────────────── │                      │                       │ ─────────────────►│
  │                    │                      │                       │                    │
  │                    │                      │                       │  7. 返回仓库数据   │
  │                    │                      │                       │ ◄─────────────────│
  │                    │                      │                       │                    │
  │                    │                      │  8. Project Profiler  │                    │
  │                    │                      │ ◄─────────────────────│                    │
  │                    │                      │     生成 ProjectProfile                   │
  │                    │                      │                       │                    │
  │                    │                      │  9. Repo Mapper       │                    │
  │                    │                      │ ◄─────────────────────│                    │
  │                    │                      │     生成 RepoMap       │                    │
  │                    │                      │                       │                    │
  │                    │  10. WebSocket 推送  │                       │                    │
  │                    │ ◄────────────────────│                       │                    │
  │                    │     项目就绪通知      │                       │                    │
  │  11. 显示项目详情  │                      │                       │                    │
  │ ◄───────────────── │                      │                       │                    │
  ▼                    ▼                      ▼                       ▼                    ▼
```

#### 核心步骤详解

##### Step 1-4: 项目创建请求

**Request:**

```json
{
  "repo_url": "https://github.com/langchain-ai/langgraph",
  "learning_goals": ["architecture", "agent_harness", "state_management"],
  "capability_modules": ["Agent Harness", "插件系统", "状态管理"],
  "archetype": "agent_framework"
}
```

**Backend 处理流程：**

```
ProjectService.create_project()
  ├─ 验证仓库 URL 格式
  ├─ 检查用户配额
  ├─ 创建 Project 实体 (状态: PENDING)
  ├─ 发送 Celery 任务: analyze_project
  └─ 返回 project_id
```

**Response:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "project_id": "proj_abc123",
    "status": "processing",
    "estimated_time": 120
  }
}
```

##### Step 5-9: 异步项目分析

**Celery Task: analyze_project**

```
analyze_project(project_id)
  ├─ GitService.clone_repo(repo_url)
  │     └─ 克隆仓库到 MinIO 存储
  │
  ├─ ProjectProfiler.analyze()
  │     ├─ 识别语言/框架
  │     ├─ 扫描目录结构
  │     ├─ 提取配置文件
  │     └─ 输出: ProjectProfile
  │
  ├─ RepoMapper.map()
  │     ├─ TreeSitter 解析 AST
  │     ├─ 构建模块列表
  │     ├─ 识别核心类/方法
  │     ├─ 识别能力模块候选
  │     └─ 输出: RepoMap + CapabilityCandidates
  │
  ├─ CodeIndexer.index()
  │     ├─ 向量化代码片段
  │     └─ 存储到 Qdrant
  │
  └─ 更新 Project 状态为 READY
```

### 4.2 学习会话流程

#### 时序图

```
用户                 Frontend              Backend                 LangGraph
  │                    │                      │                       │
  │  1. 开始学习       │                      │                       │
  │ ─────────────────► │                      │                       │
  │                    │  2. POST /sessions   │                       │
  │                    │ ────────────────────►│                       │
  │                    │                      │                       │
  │                    │                      │  3. 创建会话状态       │
  │                    │                      │ ─────────────────────►│
  │                    │                      │                       │
  │                    │                      │  4. Question Planner  │
  │                    │                      │ ◄─────────────────────│
  │                    │                      │     生成 QuestionGraph│
  │                    │                      │                       │
  │                    │                      │  5. Analysis Generator│
  │                    │                      │ ◄─────────────────────│
  │                    │                      │     生成初稿分析文档   │
  │                    │                      │                       │
  │                    │  6. 返回会话数据     │                       │
  │                    │ ◄────────────────────│                       │
  │                    │                       │                       │
  │  7. 显示学习面板   │                       │                       │
  │ ◄───────────────── │                       │                       │
  │  - 问题列表        │                       │                       │
  │  - 学习阶段        │                       │                       │
  │  - 能力模块        │                       │                       │
  ▼                    ▼                       ▼                       ▼
```

**Session Response:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "session_id": "sess_xyz789",
    "project_id": "proj_abc123",
    "learning_mode": "macro",
    "stages": [
      {
        "id": "stage_1",
        "name": "整体架构分析",
        "questions_count": 5,
        "status": "current"
      },
      {
        "id": "stage_2", 
        "name": "各模块职责与内部关系",
        "questions_count": 8,
        "status": "pending"
      }
    ],
    "capability_modules": [
      {
        "id": "cap_agent",
        "name": "Agent Harness",
        "files": ["src/agent/", "src/workflow/"],
        "status": "selected"
      }
    ],
    "current_question": {
      "id": "q_001",
      "title": "项目整体架构是什么？",
      "description": "请描述这个项目的主要模块和它们之间的关系",
      "stage": "整体架构分析",
      "recommended_files": ["src/", "README.md"]
    }
  }
}
```

### 4.3 问题驱动学习流程 (Socratic Tutoring)

#### 时序图

```
用户                 Frontend              Backend                 Tutor Agent          Explainer Agent
  │                    │                      │                       │                    │
  │  1. 查看问题       │                      │                       │                    │
  │ ◄───────────────── │                      │                       │                    │
  │                    │                      │                       │                    │
  │  2. 提交回答       │                      │                       │                    │
  │ ─────────────────► │                      │                       │                    │
  │                    │  3. POST /answers    │                       │                    │
  │                    │ ────────────────────►│                       │                    │
  │                    │                      │                       │                    │
  │                    │                      │  4. 评估回答          │                    │
  │                    │                      │ ─────────────────────►│                    │
  │                    │                      │                       │                    │
  │                    │                      │  5. 检索相关代码      │                    │
  │                    │                      │ ─────────────────────────────────────────►│
  │                    │                      │                       │                    │
  │                    │                      │  6. 生成标准讲解      │                    │
  │                    │                      │ ◄─────────────────────────────────────────│
  │                    │                      │                       │                    │
  │                    │                      │  7. 对比评估 + 纠偏   │                    │
  │                    │                      │ ◄─────────────────────│                    │
  │                    │                      │                       │                    │
  │                    │  8. 返回反馈         │                       │                    │
  │                    │ ◄────────────────────│                       │                    │
  │                    │                       │                       │                    │
  │  9. 显示反馈       │                       │                       │                    │
  │ ◄───────────────── │                       │                       │                    │
  │  - 正确点          │                       │                       │                    │
  │  - 不完整/错误点   │                       │                       │                    │
  │  - 推荐查看代码    │                       │                       │                    │
  │  - 标准答案        │                       │                       │                    │
  ▼                    ▼                       ▼                       ▼                    ▼
```

**Answer Request:**

```json
{
  "session_id": "sess_xyz789",
  "question_id": "q_001",
  "user_answer": "这个项目采用了分层架构，主要包括 API 层、服务层和数据层...",
  "time_spent": 300
}
```

**Feedback Response:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "evaluation": {
      "score": 75,
      "correct_points": [
        "正确识别了分层架构",
        "API 层的理解基本正确"
      ],
      "incomplete_points": [
        "缺少对 Agent 编排层的说明",
        "没有提到状态管理机制"
      ],
      "incorrect_points": []
    },
    "explanation": {
      "summary": "这个项目采用了 LangGraph 作为 Agent 编排框架...",
      "code_references": [
        {
          "file": "src/orchestrator/graph.py",
          "lines": [45, 78],
          "snippet": "class AgentGraph:\n    def __init__(self)...",
          "explanation": "这是核心的 Agent 状态图定义"
        }
      ],
      "key_insights": [
        "状态通过 TypedDict 定义，支持类型检查",
        "Agent 间通过 Handoff 机制传递控制"
      ]
    },
    "next_action": {
      "type": "next_question",
      "question_id": "q_002"
    },
    "progress": {
      "stage_progress": 20,
      "total_progress": 5
    }
  }
}
```

### 4.4 异常处理流程

```
正常流程                          异常流程
    │                                │
    ├─ 仓库克隆 ─────────────────► ├─ 克隆失败
    │                                │     │
    │                                │     ├─ 重试 (最多 3 次)
    │                                │     │
    │                                │     └─ 返回错误: REPO_CLONE_FAILED
    │                                │
    ├─ 代码分析 ─────────────────► ├─ 分析超时
    │                                │     │
    │                                │     ├─ 部分结果保存
    │                                │     │
    │                                │     └─ 标记: PARTIAL_ANALYSIS
    │                                │
    ├─ LLM 调用 ─────────────────► ├─ LLM 服务不可用
    │                                │     │
    │                                │     ├─ 降级到备用模型
    │                                │     │
    │                                │     └─ 返回缓存结果 (如有)
    │                                │
    ├─ 向量搜索 ─────────────────► ├─ Qdrant 连接失败
    │                                │     │
    │                                │     ├─ 降级到关键词搜索
    │                                │     │
    │                                │     └─ 记录告警日志
    │                                │
    └─ 返回成功                      └─ 返回失败 + 详细错误码

错误码定义:
┌─────────────────┬────────┬────────────────────────────┐
│ 错误码          │ HTTP   │ 描述                       │
├─────────────────┼────────┼────────────────────────────┤
│ REPO_NOT_FOUND  │ 404    │ 仓库不存在或无权限访问     │
│ REPO_TOO_LARGE  │ 413    │ 仓库超出大小限制           │
│ ANALYSIS_FAILED │ 500    │ 代码分析失败               │
│ LLM_UNAVAILABLE │ 503    │ LLM 服务暂时不可用         │
│ QUOTA_EXCEEDED  │ 429    │ 用户配额已用完             │
│ SESSION_EXPIRED │ 401    │ 学习会话已过期             │
└─────────────────┴────────┴────────────────────────────┘
```

---

## 5. 数据流向详解

### 5.1 项目分析数据流

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Git 仓库      │───►│ Project Profiler│───►│   Repo Mapper   │───►│  Question       │
│                 │    │                 │    │                 │    │  Planner        │
│ - 源代码        │    │ - 语言识别      │    │ - AST 解析      │    │ - 问题实例化    │
│ - 配置文件      │    │ - 框架检测      │    │ - 模块识别      │    │ - 依赖排序      │
│ - README        │    │ - 目录分析      │    │ - 符号提取      │    │ - 图构建        │
└─────────────────┘    └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
                                │                      │                      │
                                ▼                      ▼                      ▼
                       ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                       │ ProjectProfile  │    │    RepoMap      │    │ QuestionGraph   │
                       │ (JSON)          │    │  (JSON)         │    │  (JSON)         │
                       │                 │    │                 │    │                 │
                       │ - archetype     │    │ - modules[]     │    │ - nodes[]       │
                       │ - language      │    │ - core_classes[]│    │ - edges[]       │
                       │ - framework     │    │ - entry_points[]│    │ - stages[]      │
                       │ - dependencies  │    │ - capabilities[]│    │                 │
                       └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
                                │                      │                      │
                                └──────────────────────┼──────────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   PostgreSQL    │
                                              │   (持久化)      │
                                              └─────────────────┘
```

### 5.2 代码索引数据流

```
┌─────────────────┐
│   源代码文件    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Tree-Sitter     │
│ AST 解析器      │
│                 │
│ 支持语言:       │
│ - Python        │
│ - TypeScript    │
│ - Java          │
│ - Go            │
│ - Rust          │
└────────┬────────┘
         │
         ├────────────────────────┬────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  符号索引       │    │  代码片段       │    │  调用关系       │
│                 │    │                 │    │                 │
│ - 类名          │    │ - 函数体        │    │ - 调用图        │
│ - 函数名        │    │ - 类定义        │    │ - 依赖图        │
│ - 变量名        │    │ - 注释          │    │ - 继承关系      │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         ▼                      ▼                      │
┌─────────────────┐    ┌─────────────────┐             │
│ PostgreSQL      │    │ Embedding 服务  │             │
│ (结构化搜索)    │    │ (向量化)        │             │
│                 │    │                 │             │
│ symbols 表      │    │ OpenAI / Local  │             │
└─────────────────┘    └────────┬────────┘             │
                                │                      │
                                ▼                      │
                       ┌─────────────────┐             │
                       │    Qdrant       │◄────────────┘
                       │ (向量存储)      │
                       │                 │
                       │ collections:    │
                       │ - code_chunks   │
                       │ - doc_chunks    │
                       └─────────────────┘
```

### 5.3 学习流程数据流

```
┌──────────────────────────────────────────────────────────────────────┐
│                       完整学习流程数据流                              │
└──────────────────────────────────────────────────────────────────────┘

1. 项目初始化阶段
   User
      │
      ├─ POST /projects ────────────► Backend ────► Celery Task
      │     { repo_url, goals }              │
      │                                      ├─ GitService.clone()
      │                                      ├─ ProjectProfiler.analyze()
      │                                      ├─ RepoMapper.map()
      │                                      ├─ CodeIndexer.index()
      │                                      └─ 存储到 DB + Qdrant

2. 会话创建阶段
   User
      │
      └─ POST /sessions ───────────► Backend
           { project_id, mode }         │
                                        ├─ 加载 ProjectProfile (DB)
                                        ├─ 加载 RepoMap (DB)
                                        ├─ QuestionPlanner.plan()
                                        ├─ AnalysisGenerator.generate()
                                        └─ 返回 Session + QuestionGraph

3. 问题回答阶段
   User ◄────────► Frontend ◄────────► Backend (LangGraph)
      │                                   │
      │ 提交回答                          ├─ TutorAgent.evaluate()
      │                                   │     └─ 用户回答 vs 标准答案
      │                                   │
      │                                   ├─ ExplainerAgent.explain()
      │                                   │     └─ 检索代码 + 生成讲解
      │                                   │
      │ 接收反馈                          ├─ NoteManager.record()
      │                                   │     └─ 保存 QA 记录
      │                                   │
      │                                   └─ ProgressTracker.update()
      │                                         └─ 更新学习进度

4. 文档导出阶段
   User
      │
      └─ GET /analysis/export ────► Backend
                                      │
                                      ├─ 加载分析文档 (DB)
                                      ├─ 合并用户笔记
                                      ├─ 格式化输出 (Markdown/HTML)
                                      └─ 上传到 MinIO + 返回下载链接
```

---

## 6. 关键组件详解

### 6.1 Project Profiler（项目画像器）

#### 6.1.1 组件职责

- 克隆/加载代码仓库
- 分析编程语言和框架特征
- 识别项目原型（archetype）
- 扫描目录结构，识别各层职责
- 提取项目配置和依赖信息

#### 6.1.2 核心接口

```python
class ProjectProfiler:
    """项目画像生成器 - 生成项目的结构化元数据"""
    
    async def analyze(self, repo_path: str) -> ProjectProfile:
        """
        分析仓库并生成项目画像
        
        Args:
            repo_path: 仓库本地路径
        
        Returns:
            ProjectProfile 值对象
        """
        pass
    
    def detect_archetype(self, profile: ProjectProfile) -> str:
        """
        识别项目原型类型
        
        Returns:
            archetype: web_backend | library | agent_framework | 
                      rag_system | frontend_spa | cli_tool
        """
        pass
    
    def extract_entry_points(self, repo_path: str) -> List[EntryPoint]:
        """提取项目入口点"""
        pass
```

#### 6.1.3 输出数据结构

```json
{
  "project_id": "proj_abc123",
  "archetype": "agent_framework",
  "primary_language": "python",
  "languages": {
    "python": 85.5,
    "typescript": 10.2,
    "other": 4.3
  },
  "framework": {
    "name": "langgraph",
    "version": "0.2.x",
    "confidence": 0.95
  },
  "dependencies": [
    {"name": "langchain", "version": "^0.3.0", "type": "core"},
    {"name": "langchain-core", "version": "^0.3.0", "type": "core"},
    {"name": "langchain-openai", "version": "^0.2.0", "type": "llm"},
    {"name": "langchain-anthropic", "version": "^0.2.0", "type": "llm"},
    {"name": "langchain-ollama", "version": "^0.2.0", "type": "llm"},
    {"name": "langchain-qdrant", "version": "^0.2.0", "type": "vectorstore"},
    {"name": "langchain-chroma", "version": "^0.2.0", "type": "vectorstore"},
    {"name": "langchain-huggingface", "version": "^0.1.0", "type": "embedding"},
    {"name": "fastapi", "version": "^0.109.0", "type": "api"}
  ],
  "directory_structure": {
    "api": {"type": "presentation", "files_count": 15},
    "domain": {"type": "business", "files_count": 28},
    "infrastructure": {"type": "infra", "files_count": 22}
  },
  "entry_points": [
    {"file": "main.py", "type": "application", "description": "FastAPI 应用入口"},
    {"file": "src/graph.py", "type": "core", "description": "Agent 状态图定义"}
  ],
  "config_files": ["pyproject.toml", ".env.example", "docker-compose.yml"]
}
```

### 6.2 Repo Mapper（代码地图生成器）

#### 6.2.1 组件职责

- 构建代码模块映射
- 解析 AST 提取符号信息
- 识别核心类和关键方法
- 构建调用关系图
- 识别能力模块候选

#### 6.2.2 核心接口

```python
class RepoMapper:
    """代码地图生成器 - 构建仓库的结构化映射"""
    
    def __init__(self, parser: TreeSitterParser, indexer: CodeIndexer):
        self.parser = parser
        self.indexer = indexer
    
    async def map(self, repo_path: str, profile: ProjectProfile) -> RepoMap:
        """
        构建仓库代码地图
        
        Args:
            repo_path: 仓库路径
            profile: 项目画像
        
        Returns:
            RepoMap 包含模块、类、方法、依赖关系
        """
        pass
    
    def identify_capabilities(self, repo_map: RepoMap) -> List[CapabilityCandidate]:
        """
        识别能力模块候选
        
        识别逻辑:
        - 目录命名: plugins/, auth/, cache/, workflow/
        - 框架模式: middleware 管道, 事件总线
        - 依赖特征: redis (缓存), celery (任务队列)
        """
        pass
    
    def build_call_graph(self, symbols: List[Symbol]) -> CallGraph:
        """构建函数/方法调用图"""
        pass
```

#### 6.2.3 输出数据结构

```json
{
  "repo_id": "repo_abc123",
  "modules": [
    {
      "name": "orchestrator",
      "path": "src/orchestrator/",
      "type": "core",
      "description": "Agent 状态图编排",
      "files": ["graph.py", "nodes.py", "state.py"],
      "dependencies": ["domain", "infrastructure.llm"]
    }
  ],
  "core_classes": [
    {
      "name": "AgentGraph",
      "file": "src/orchestrator/graph.py",
      "lines": [45, 120],
      "methods": ["build", "compile", "invoke"],
      "importance": "high",
      "description": "核心状态图构建类"
    }
  ],
  "key_methods": [
    {
      "name": "process_message",
      "class": "TutorAgent",
      "file": "src/agents/tutor.py",
      "lines": [78, 145],
      "calls": ["evaluate_answer", "generate_feedback"],
      "called_by": ["AgentGraph.invoke"]
    }
  ],
  "capability_candidates": [
    {
      "name": "Agent Harness",
      "confidence": 0.92,
      "directories": ["src/orchestrator/", "src/agents/"],
      "key_files": ["graph.py", "state.py"],
      "patterns_detected": ["StateGraph", "Handoff", "ToolNode"]
    },
    {
      "name": "插件系统",
      "confidence": 0.78,
      "directories": ["src/plugins/"],
      "key_files": ["base.py", "registry.py"],
      "patterns_detected": ["PluginBase", "register_plugin"]
    }
  ]
}
```

### 6.3 Question Planner（问题规划器）

#### 6.3.1 组件职责

- 从问题模版库选择适用模版
- 根据项目特征实例化问题
- 构建问题依赖图（QuestionGraph）
- 动态调整问题序列

#### 6.3.2 核心接口

```python
class QuestionPlanner:
    """问题规划器 - 生成个性化问题序列"""
    
    def __init__(self, template_repo: QuestionTemplateRepository):
        self.template_repo = template_repo
    
    async def plan(
        self,
        profile: ProjectProfile,
        repo_map: RepoMap,
        learning_goals: List[str],
        selected_capabilities: List[str]
    ) -> QuestionGraph:
        """
        生成问题图
        
        Args:
            profile: 项目画像
            repo_map: 代码地图
            learning_goals: 学习目标
            selected_capabilities: 选中的能力模块
        
        Returns:
            QuestionGraph 问题有向图
        """
        pass
    
    def instantiate_template(
        self,
        template: QuestionTemplate,
        context: Dict
    ) -> Question:
        """
        实例化问题模版
        
        将模版占位符替换为实际值:
        {files} -> 具体文件路径
        {entry_fn} -> 入口函数名
        {module_name} -> 模块名称
        """
        pass
    
    def select_next_question(
        self,
        graph: QuestionGraph,
        progress: UserProgress
    ) -> Optional[Question]:
        """根据进度选择下一个问题"""
        pass
```

#### 6.3.3 问题模版示例

```yaml
# templates/questions/agent_framework/architecture.yaml
id: agent_arch_001
archetype: agent_framework
stage: 整体架构分析
difficulty: medium

title_template: "项目的 Agent 编排架构是如何设计的？"
description_template: |
  请分析 {project_name} 的 Agent 编排架构:
  1. 核心的状态图定义在哪里？
  2. Agent 之间如何通信？
  3. 状态是如何管理和持久化的？

placeholders:
  - project_name
  - entry_file
  - state_file

recommended_files:
  - "{entry_file}"
  - "{state_file}"
  - "src/orchestrator/"

prerequisites:
  - agent_arch_000  # 必须先回答基础架构问题

tags:
  - architecture
  - langgraph
  - state_management
```

### 6.4 Analysis Generator（分析文档生成器）

#### 6.4.1 组件职责

- 按九大章节模版生成分析文档
- 基于代码检索生成内容（RAG）
- 支持增量更新和版本管理
- 生成多格式输出（Markdown/HTML/PDF）

#### 6.4.2 九大章节模版

| 章节 | 内容要点 | 数据来源 |
|------|----------|----------|
| 1. 整体架构分析 | 分层架构、模块划分、设计风格 | ProjectProfile, RepoMap |
| 2. 各模块职责与内部关系 | 模块职责、依赖关系、接口 | RepoMap.modules |
| 3. 核心类解剖 | 核心类结构、职责、关键属性 | RepoMap.core_classes |
| 4. 关键方法深度解析 | 算法逻辑、参数说明、返回值 | RepoMap.key_methods + 代码检索 |
| 5. 模块间调用依赖关系 | 调用图、依赖方向、循环检测 | CallGraph |
| 6. 核心流程分析 | 主要用例流程、时序图 | 代码检索 + LLM 生成 |
| 7. 核心入口 & 主要数据流 | 入口点、数据流转、状态变化 | EntryPoints + 代码分析 |
| 8. 设计亮点与精妙之处 | 设计模式、最佳实践、创新点 | LLM 分析 + 代码检索 |
| 9. 从源码看最佳实践 | 代码风格、工程实践、可借鉴点 | 代码检索 + LLM 总结 |

#### 6.4.3 核心接口

```python
class AnalysisGenerator:
    """分析文档生成器 - 生成结构化项目分析"""
    
    def __init__(
        self,
        llm: BaseChatModel,           # LangChain ChatModel
        vector_store: VectorStore,     # LangChain VectorStore
        template_engine: TemplateEngine
    ):
        self.llm = llm
        self.vector_store = vector_store
        self.retriever = vector_store.as_retriever()  # LangChain Retriever
        self.templates = template_engine
    
    async def generate(
        self,
        profile: ProjectProfile,
        repo_map: RepoMap,
        selected_sections: List[str] = None
    ) -> AnalysisDocument:
        """
        生成分析文档
        
        Args:
            profile: 项目画像
            repo_map: 代码地图
            selected_sections: 指定章节 (默认全部)
        
        Returns:
            AnalysisDocument 结构化分析文档
        """
        pass
    
    async def generate_section(
        self,
        section_id: str,
        context: AnalysisContext
    ) -> Section:
        """生成单个章节内容"""
        pass
    
    def export(
        self,
        document: AnalysisDocument,
        format: str = "markdown"
    ) -> str:
        """导出为指定格式"""
        pass
```

### 6.5 Tutor Agent（学习教练智能体）

#### 6.5.1 组件职责

- 驱动问题驱动的学习流程
- 评估用户回答质量
- 提供苏格拉底式引导
- 控制知识披露节奏

#### 6.5.2 DeepAgents SubAgent 定义

```python
from deepagents import SubAgent
from deepagents.tools import tool

# 定义 Tutor 专用工具
@tool
def evaluate_answer(
    user_answer: str,
    question_id: str,
    reference_answer: str
) -> dict:
    """
    评估用户回答质量
    
    评估维度:
    - 正确性: 与标准答案对比
    - 完整性: 是否涵盖关键点
    - 深度: 理解程度
    
    Returns:
        包含 score, correct_points, incomplete_points, incorrect_points
    """
    # 实现评估逻辑
    pass

@tool
def generate_socratic_feedback(
    evaluation: dict,
    question_context: str
) -> dict:
    """
    生成苏格拉底式反馈
    
    策略:
    - 先肯定正确部分
    - 指出不完整/错误的点
    - 引导思考而非直接给答案
    - 推荐查看的代码位置
    """
    pass

@tool
def delegate_to_explainer(
    question_id: str,
    user_gaps: list
) -> str:
    """
    委托 Explainer 子Agent 生成代码讲解
    
    Args:
        question_id: 问题ID
        user_gaps: 用户回答中缺失的知识点
    
    Returns:
        详细的代码讲解内容
    """
    pass

# 定义 Tutor SubAgent
tutor_subagent = SubAgent(
    name="tutor",
    description="学习教练 - 评估用户回答并提供苏格拉底式引导反馈",
    system_prompt="""你是一位资深的编程导师，专注于帮助开发者理解开源项目。

你的教学风格:
1. 苏格拉底式提问 - 先让用户思考，再给予引导
2. 循序渐进 - 从整体到细节，从简单到复杂
3. 代码为证 - 所有解释必须基于实际代码
4. 积极鼓励 - 肯定用户的正确理解，温和指出不足

当用户回答问题后:
1. 先评估回答的正确性和完整性
2. 指出哪些理解是正确的（给予肯定）
3. 对于不完整的部分，给出提示而非直接答案
4. 如果有错误，温和地纠正并解释原因
5. 推荐用户查看相关代码位置
""",
    tools=[
        evaluate_answer,
        generate_socratic_feedback,
        delegate_to_explainer,
    ],
    # 可以有自己的中间件配置
    interrupt_on=["generate_socratic_feedback"],  # 敏感操作时可暂停
)
```

#### 6.5.3 Tutor 与主 Agent 的集成

```python
from deepagents import create_deep_agent, SubAgent

# 主 Agent 通过 task() 工具调用 Tutor SubAgent
# 调用示例 (主 Agent 内部):
# result = task("tutor", "请评估用户对架构问题的回答: ...")

# Tutor SubAgent 的上下文与主 Agent 隔离
# 只返回最终反馈结果，不污染主 Agent 上下文
```

### 6.6 Explainer Agent（代码讲解智能体）

#### 6.6.1 组件职责

- 基于代码检索生成讲解
- 引用具体文件和行号
- 保证内容准确性（RAG 约束）
- 生成可定位的代码引用

#### 6.6.2 核心接口

```python
class ExplainerAgent:
    """代码讲解智能体 - 生成基于代码的准确讲解"""
    
    def __init__(
        self,
        llm: BaseChatModel,             # LangChain ChatModel
        vector_store: VectorStore,       # LangChain VectorStore
        code_search: CodeSearchService
    ):
        self.llm = llm
        self.vector_store = vector_store
        self.retriever = vector_store.as_retriever()  # LangChain Retriever
        self.code_search = code_search
    
    async def explain(
        self,
        question: Question,
        evaluation: Evaluation
    ) -> Explanation:
        """
        生成代码讲解
        
        流程:
        1. 根据问题检索相关代码片段
        2. 结合分析文档获取上下文
        3. 生成讲解 (必须引用具体代码)
        4. 验证引用准确性
        """
        # 1. 语义检索
        relevant_chunks = await self.vector_store.search(
            query=question.description,
            filter={"project_id": question.project_id},
            top_k=10
        )
        
        # 2. 符号搜索补充
        symbol_results = await self.code_search.search_symbols(
            keywords=question.keywords,
            project_id=question.project_id
        )
        
        # 3. 生成讲解
        prompt = self._build_explanation_prompt(
            question=question,
            code_chunks=relevant_chunks,
            symbols=symbol_results,
            user_gaps=evaluation.incomplete_points
        )
        
        explanation = await self.llm.generate(
            prompt,
            system_prompt=EXPLAINER_SYSTEM_PROMPT
        )
        
        # 4. 验证引用
        validated = self._validate_references(explanation)
        
        return validated

EXPLAINER_SYSTEM_PROMPT = """
你是一个代码讲解助手。请基于提供的代码片段生成讲解。

规则:
1. 必须引用具体的文件路径和行号
2. 不要编造不存在的代码
3. 如果信息不足，明确说明
4. 使用代码块展示关键代码
5. 解释代码的设计意图，而不仅仅是描述代码做什么
"""
```

### 6.7 Note & Progress Manager（笔记与进度管理）

#### 6.7.1 组件职责

- 记录问答过程
- 跟踪学习进度
- 管理用户笔记
- 支持多设备同步

#### 6.7.2 数据模型

```python
class LearningRecord(Entity):
    """学习记录实体"""
    id: str
    session_id: str
    question_id: str
    user_answer: str
    evaluation: Evaluation
    explanation: Explanation
    user_notes: Optional[str]
    time_spent: int  # 秒
    created_at: datetime

class UserProgress(Entity):
    """用户进度实体"""
    user_id: str
    project_id: str
    session_id: str
    
    # 阶段进度
    completed_stages: List[str]
    current_stage: str
    
    # 问题进度
    answered_questions: List[str]
    correct_questions: List[str]
    
    # 能力模块进度
    capability_progress: Dict[str, float]  # module_id -> completion %
    
    # 统计
    total_time_spent: int
    average_score: float
    last_active_at: datetime
```

### 6.8 组件间依赖关系

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DeepAgents Main Agent + Middleware                    │
│                                                                          │
│    ┌──────────────┐                                                     │
│    │   Project    │                                                     │
│    │   Profiler   │──────────────────────┐                              │
│    └──────┬───────┘                      │                              │
│           │                              │                              │
│           ▼                              ▼                              │
│    ┌──────────────┐              ┌──────────────┐                       │
│    │    Repo      │──────────────│   Question   │                       │
│    │    Mapper    │              │   Planner    │                       │
│    └──────┬───────┘              └──────┬───────┘                       │
│           │                              │                              │
│           │         ┌────────────────────┼────────────────────┐        │
│           │         │                    │                    │        │
│           ▼         ▼                    ▼                    ▼        │
│    ┌──────────────────────┐      ┌──────────────┐    ┌──────────────┐  │
│    │     Analysis         │      │    Tutor     │    │    Note &    │  │
│    │     Generator        │◄─────│    Agent     │───►│   Progress   │  │
│    └──────────┬───────────┘      └──────┬───────┘    │   Manager    │  │
│               │                         │            └──────────────┘  │
│               │                         │                              │
│               │                         ▼                              │
│               │                  ┌──────────────┐                      │
│               └─────────────────►│   Explainer  │                      │
│                                  │    Agent     │                      │
│                                  └──────────────┘                      │
└─────────────────────────────────────────────────────────────────────────┘
                    │                     │
                    ▼                     ▼
            ┌──────────────┐      ┌──────────────┐
            │  LLM Client  │      │ Vector Store │
            │ (OpenAI等)   │      │  (Qdrant)    │
            └──────────────┘      └──────────────┘
```

---

## 7. 技术选型说明

### 7.1 关键设计模式

| 模式 | 实现位置 | 优势 |
|------|----------|------|
| **DDD 分层** | 整体架构 | 业务逻辑清晰，易于测试和维护 |
| **中间件架构** | DeepAgents Middleware | 功能模块化，可组合扩展 |
| **SubAgent 模式** | SubAgentMiddleware | 上下文隔离，任务委托，防止污染 |
| **任务规划模式** | TodoListMiddleware | 复杂任务分解，进度跟踪 |
| **虚拟文件系统** | FilesystemMiddleware | 长期记忆，上下文 offload |
| **RAG 模式** | Explainer Agent | 基于检索生成，保证准确性 |
| **Repository** | 数据访问 | 数据访问抽象，易于替换实现 |
| **模版方法** | 问题/分析生成 | 标准化流程，支持定制 |

### 7.2 核心通信协议

| 协议 | 用途 | 端点 |
|------|------|------|
| **HTTP/REST** | 同步 API 请求 | Backend:8000/api/v1/* |
| **WebSocket** | 实时对话、进度推送 | Backend:8000/ws/agents/{session_id} |
| **gRPC** | 代码索引服务 (可选) | CodeIndexer:50051 |
| **Redis Pub/Sub** | 异步事件通知 | Redis:6379 |

### 7.3 技术栈对比

| 组件 | 选择方案 | 备选方案 | 选择理由 |
|------|----------|----------|----------|
| **后端框架** | FastAPI | Django | 异步性能好，类型提示友好 |
| **Agent 框架** | DeepAgents | LangGraph, AutoGen | 内置中间件，开箱即用，基于 LangGraph |
| **LLM 封装层** | LangChain | 直接调用 API | 统一接口，易于切换模型，内置 Prompt 模版 |
| **LLM 服务** | OpenAI GPT-4 | Claude, 本地 LLM | 综合能力强，API 稳定 |
| **向量库封装** | LangChain VectorStore | 直接调用 SDK | 统一接口，支持多种向量库切换 |
| **向量数据库** | Qdrant | ChromaDB, Milvus | 性能好，过滤功能强 |
| **Embedding** | LangChain Embeddings | 直接调用 API | 统一接口，支持多种 Embedding 模型 |
| **主数据库** | PostgreSQL | MySQL | JSON 支持好，扩展性强 |
| **缓存** | Redis | Memcached | 数据结构丰富，支持 Pub/Sub |
| **任务队列** | Celery + Redis | RQ, Dramatiq | 生态成熟，监控完善 |
| **代码解析** | tree-sitter | AST 模块 | 多语言支持，增量解析 |
| **对象存储** | MinIO | S3, OSS | 自托管，S3 兼容 |

### 7.4 LangChain 集成架构

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            LangChain 统一封装层                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                         LLM / Chat Models                                │    │
│  │                                                                          │    │
│  │  from langchain_openai import ChatOpenAI                                │    │
│  │  from langchain_anthropic import ChatAnthropic                          │    │
│  │  from langchain_ollama import ChatOllama                                │    │
│  │                                                                          │    │
│  │  # 统一接口，一行代码切换模型                                            │    │
│  │  llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)                   │    │
│  │  llm = ChatAnthropic(model="claude-3-opus")                             │    │
│  │  llm = ChatOllama(model="llama3")  # 本地部署                           │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                         Embeddings                                       │    │
│  │                                                                          │    │
│  │  from langchain_openai import OpenAIEmbeddings                          │    │
│  │  from langchain_huggingface import HuggingFaceEmbeddings                │    │
│  │                                                                          │    │
│  │  # 统一接口                                                              │    │
│  │  embeddings = OpenAIEmbeddings(model="text-embedding-3-small")          │    │
│  │  embeddings = HuggingFaceEmbeddings(model="BAAI/bge-small-zh")          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                         Vector Stores                                    │    │
│  │                                                                          │    │
│  │  from langchain_qdrant import QdrantVectorStore                         │    │
│  │  from langchain_chroma import Chroma                                    │    │
│  │  from langchain_postgres import PGVector                                │    │
│  │                                                                          │    │
│  │  # 统一接口，一行代码切换向量库                                          │    │
│  │  vectorstore = QdrantVectorStore.from_documents(docs, embeddings)       │    │
│  │  vectorstore = Chroma.from_documents(docs, embeddings)                  │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                         RAG Components                                   │    │
│  │                                                                          │    │
│  │  from langchain.text_splitter import RecursiveCharacterTextSplitter     │    │
│  │  from langchain.retrievers import ContextualCompressionRetriever        │    │
│  │  from langchain.chains import RetrievalQA                               │    │
│  │                                                                          │    │
│  │  # 开箱即用的 RAG 组件                                                   │    │
│  │  retriever = vectorstore.as_retriever(search_kwargs={"k": 10})          │    │
│  │  chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)      │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            DeepAgents (基于 LangGraph)                           │
│                                                                                  │
│  # DeepAgents 内部使用 LangChain 的 LLM                                         │
│  coach = create_deep_agent(                                                     │
│      model=ChatOpenAI(model="gpt-4-turbo"),  # LangChain ChatModel             │
│      ...                                                                        │
│  )                                                                              │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### 使用 LangChain 的优势

| 优势 | 说明 |
|------|------|
| **统一接口** | 切换 LLM 只需改一行代码，无需修改业务逻辑 |
| **丰富生态** | 支持 50+ LLM 提供商，20+ 向量库 |
| **内置组件** | Text Splitter、Retriever、Chain 等开箱即用 |
| **Prompt 模版** | 结构化 Prompt 管理，支持变量替换 |
| **回调机制** | 内置日志、追踪、流式输出支持 |
| **与 DeepAgents 兼容** | DeepAgents 原生支持 LangChain 组件 |

#### LangChain 初始化示例

```python
# infrastructure/langchain/llm.py
"""LLM 配置 - 通过 LangChain 统一封装"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel

from core.config import settings


def get_llm(provider: str = None) -> BaseChatModel:
    """
    获取 LLM 实例 - 统一接口，一行代码切换模型
    
    Args:
        provider: 模型提供商 (openai, anthropic, ollama)
    
    Returns:
        BaseChatModel: LangChain ChatModel 实例
    """
    provider = provider or settings.llm.provider
    
    if provider == "openai":
        return ChatOpenAI(
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            api_key=settings.openai.api_key,
        )
    elif provider == "anthropic":
        return ChatAnthropic(
            model=settings.llm.model,
            api_key=settings.anthropic.api_key,
        )
    elif provider == "ollama":
        return ChatOllama(
            model=settings.llm.model,
            base_url=settings.ollama.base_url,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


# infrastructure/langchain/embeddings.py
"""Embedding 配置 - 通过 LangChain 统一封装"""

from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings

from core.config import settings


def get_embeddings(provider: str = None) -> Embeddings:
    """
    获取 Embedding 实例
    """
    provider = provider or settings.embedding.provider
    
    if provider == "openai":
        return OpenAIEmbeddings(
            model=settings.embedding.model,
            api_key=settings.openai.api_key,
        )
    elif provider == "huggingface":
        return HuggingFaceEmbeddings(
            model_name=settings.embedding.model,
        )
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")


# infrastructure/langchain/vectorstore.py
"""向量库配置 - 通过 LangChain 统一封装"""

from langchain_qdrant import QdrantVectorStore
from langchain_chroma import Chroma
from langchain_postgres import PGVector
from langchain_core.vectorstores import VectorStore

from qdrant_client import QdrantClient
from core.config import settings
from .embeddings import get_embeddings


def get_vectorstore(
    collection_name: str,
    provider: str = None
) -> VectorStore:
    """
    获取向量库实例 - 统一接口，一行代码切换向量库
    
    Args:
        collection_name: 集合名称
        provider: 向量库提供商 (qdrant, chroma, pgvector)
    """
    provider = provider or settings.vectorstore.provider
    embeddings = get_embeddings()
    
    if provider == "qdrant":
        client = QdrantClient(
            url=settings.qdrant.url,
            api_key=settings.qdrant.api_key,
        )
        return QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )
    elif provider == "chroma":
        return Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=settings.chroma.persist_dir,
        )
    elif provider == "pgvector":
        return PGVector(
            collection_name=collection_name,
            embeddings=embeddings,
            connection=settings.database.url,
        )
    else:
        raise ValueError(f"Unsupported vectorstore provider: {provider}")


# infrastructure/langchain/retrievers.py
"""Retriever 配置 - RAG 检索组件"""

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_core.retrievers import BaseRetriever

from .llm import get_llm
from .vectorstore import get_vectorstore


def get_code_retriever(
    project_id: str,
    search_k: int = 10
) -> BaseRetriever:
    """
    获取代码检索器
    
    Args:
        project_id: 项目 ID
        search_k: 返回文档数量
    """
    collection_name = f"code_{project_id}"
    vectorstore = get_vectorstore(collection_name)
    
    # 基础检索器
    base_retriever = vectorstore.as_retriever(
        search_type="mmr",  # Maximal Marginal Relevance
        search_kwargs={
            "k": search_k,
            "fetch_k": search_k * 2,
        }
    )
    
    # 使用 LLM 压缩和筛选结果 (可选)
    # compressor = LLMChainExtractor.from_llm(get_llm())
    # return ContextualCompressionRetriever(
    #     base_compressor=compressor,
    #     base_retriever=base_retriever,
    # )
    
    return base_retriever


# infrastructure/langchain/chains/rag_chain.py
"""RAG 检索链 - 代码问答"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from ..llm import get_llm
from ..retrievers import get_code_retriever


def create_code_qa_chain(project_id: str):
    """
    创建代码问答 RAG Chain
    """
    llm = get_llm()
    retriever = get_code_retriever(project_id)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个代码学习助手。基于以下代码片段回答用户问题。
        
代码上下文:
{context}

要求:
1. 必须引用具体代码位置
2. 解释清晰、准确
3. 使用苏格拉底式教学法"""),
        ("human", "{question}")
    ])
    
    # LangChain Expression Language (LCEL) 链
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain


# 使用示例
async def answer_question(project_id: str, question: str) -> str:
    chain = create_code_qa_chain(project_id)
    response = await chain.ainvoke(question)
    return response
```

### 7.4 DeepAgents 主 Agent 设计

```python
from deepagents import create_deep_agent, SubAgent
from deepagents.middleware import (
    TodoListMiddleware,
    FilesystemMiddleware,
    SubAgentMiddleware,
    SummarizationMiddleware,
    HumanInTheLoopMiddleware,
)

# ============================================================
# 1. 定义专用工具
# ============================================================

from deepagents.tools import tool

@tool
def clone_repository(repo_url: str) -> dict:
    """克隆 Git 仓库到本地工作空间"""
    pass

@tool
def search_code(query: str, project_id: str) -> list:
    """语义搜索代码片段"""
    pass

@tool
def get_question(question_id: str) -> dict:
    """获取问题详情和参考答案"""
    pass

# ============================================================
# 2. 定义子 Agent (SubAgents)
# ============================================================

# 项目画像子Agent
profiler_subagent = SubAgent(
    name="project-profiler",
    description="分析项目结构、识别语言框架、生成项目画像",
    system_prompt="""你是项目分析专家，负责:
    1. 识别项目的编程语言和框架
    2. 分析目录结构和模块划分
    3. 识别项目类型 (web_backend/library/agent_framework 等)
    4. 输出结构化的 ProjectProfile""",
    tools=[clone_repository],
)

# 代码地图子Agent
mapper_subagent = SubAgent(
    name="repo-mapper",
    description="构建代码地图、提取符号、识别能力模块",
    system_prompt="""你是代码分析专家，负责:
    1. 解析 AST 提取类、函数、方法
    2. 构建模块依赖关系图
    3. 识别核心类和关键方法
    4. 识别能力模块候选 (插件系统、缓存层等)""",
    tools=[search_code],
)

# 问题规划子Agent
planner_subagent = SubAgent(
    name="question-planner", 
    description="根据项目特征生成个性化问题序列",
    system_prompt="""你是教学规划专家，负责:
    1. 从问题模版库选择适用模版
    2. 根据项目特征实例化问题
    3. 构建问题依赖图
    4. 动态调整问题序列""",
)

# 分析文档生成子Agent
generator_subagent = SubAgent(
    name="analysis-generator",
    description="生成九大章节的结构化分析文档",
    system_prompt="""你是技术文档专家，负责:
    1. 按九大章节模版生成分析
    2. 基于代码检索生成内容
    3. 确保引用准确、内容有据""",
    tools=[search_code],
)

# 学习教练子Agent (核心)
tutor_subagent = SubAgent(
    name="tutor",
    description="评估用户回答、提供苏格拉底式引导反馈",
    system_prompt="""你是编程导师，采用苏格拉底式教学:
    1. 先让用户思考，再给予引导
    2. 肯定正确部分，温和指出不足
    3. 引导思考而非直接给答案
    4. 推荐查看相关代码位置""",
    tools=[get_question, search_code],
    # 敏感操作时暂停等待确认
    interrupt_on=["generate_feedback"],
)

# 代码讲解子Agent
explainer_subagent = SubAgent(
    name="explainer",
    description="基于 RAG 生成准确的代码讲解",
    system_prompt="""你是代码讲解专家，规则:
    1. 必须引用具体的文件路径和行号
    2. 不要编造不存在的代码
    3. 解释设计意图，而非仅描述功能
    4. 如信息不足，明确说明""",
    tools=[search_code],
)

# ============================================================
# 3. 创建主 Agent (Learning Coach)
# ============================================================

learning_coach = create_deep_agent(
    model="gpt-4-turbo",
    system_prompt="""你是「开源项目学习教练」，帮助开发者深入理解开源项目。

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
6. 进入学习循环:
   - tutor 提问 → 用户回答 → tutor 评估 → explainer 讲解
7. 记录学习进度和笔记

重要: 使用 write_todos 规划任务，使用 task() 委托子Agent""",
    
    # 子Agent列表
    subagents=[
        profiler_subagent,
        mapper_subagent,
        planner_subagent,
        generator_subagent,
        tutor_subagent,
        explainer_subagent,
    ],
    
    # 自定义中间件配置 (可选)
    # 默认已包含: TodoList, Filesystem, SubAgent, Summarization
    
    # 人工审批配置 (可选)
    interrupt_on=["complete_learning_session"],
)

# ============================================================
# 4. 运行示例
# ============================================================

async def main():
    # 启动学习会话
    result = await learning_coach.invoke({
        "messages": [{
            "role": "user",
            "content": """请帮我学习这个项目:
            - 仓库: https://github.com/langchain-ai/langgraph
            - 学习目标: 理解多Agent编排架构
            - 重点能力模块: Agent Harness, 状态管理"""
        }]
    })
    
    print(result)
```

### 7.5 DeepAgents vs LangGraph 对比

| 维度 | DeepAgents | LangGraph |
|------|------------|-----------|
| **抽象级别** | 高级，开箱即用 | 低级，需手动构建 |
| **内置功能** | TodoList + Filesystem + SubAgent | 需自行实现 |
| **代码量** | ~50 行创建完整 Agent | ~200+ 行构建状态图 |
| **上下文管理** | 自动隔离和摘要 | 需手动管理 |
| **学习曲线** | 较低 | 较高 |
| **灵活性** | 通过中间件扩展 | 完全可控 |
| **底层依赖** | 基于 LangGraph | 独立框架 |

**选择 DeepAgents 的原因：**
1. `TodoListMiddleware` 天然适合 Question Planner
2. `SubAgentMiddleware` 完美匹配多 Agent 协作需求
3. `FilesystemMiddleware` 解决笔记和进度持久化
4. `SummarizationMiddleware` 处理大仓库上下文溢出
5. 开发效率高，代码量少，易于维护

---

## 8. 扩展与优化建议

### 8.1 性能优化

| 优化点 | 描述 | 预期收益 | 优先级 |
|--------|------|----------|--------|
| **LLM 响应缓存** | 相同问题/代码的 LLM 响应缓存 | 减少 API 调用 50%+ | P0 |
| **增量代码索引** | 只索引变更文件 | 更新速度提升 80% | P1 |
| **向量预加载** | 项目向量预加载到内存 | 搜索延迟降低 60% | P1 |
| **流式响应** | LLM 流式输出到前端 | 首字节时间降低 70% | P1 |
| **批量嵌入** | 代码片段批量向量化 | 索引速度提升 3x | P2 |

### 8.2 可靠性设计

| 设计点 | 描述 | 实现方式 |
|--------|------|----------|
| **LLM 降级** | 主模型不可用时切换备用 | OpenAI → Claude → 本地模型 |
| **重试机制** | API 调用失败自动重试 | 指数退避，最多 3 次 |
| **超时控制** | LLM 调用超时保护 | 默认 30s，长任务 120s |
| **断点续传** | 大仓库克隆断点续传 | git shallow clone + 增量 |
| **状态持久化** | Agent 状态持久化 | DeepAgents FilesystemMiddleware + PostgreSQL |
| **幂等设计** | 任务重复执行安全 | 任务 ID + 状态检查 |

### 8.3 可观测性

| 类型 | 工具 | 说明 |
|------|------|------|
| **日志** | structlog + ELK | 结构化日志，链路追踪 |
| **指标** | Prometheus + Grafana | LLM 调用量、延迟、成功率 |
| **追踪** | OpenTelemetry + Jaeger | Agent 调用链追踪 |
| **告警** | AlertManager | LLM 配额告警、错误率告警 |
| **LLM 监控** | LangSmith / Helicone | LLM 调用分析、成本追踪 |

### 8.4 扩展性设计

```
当前架构 (MVP)                      扩展后架构 (Scale)
┌─────────────────┐                ┌─────────────────────────────────┐
│ Backend (单实例) │                │     Backend Cluster (N 实例)    │
│ + DeepAgents    │    ────────►   │     + 无状态设计                │
└─────────────────┘                │     + Redis 会话共享            │
        │                          └─────────────────────────────────┘
        ▼                                         │
┌─────────────────┐                               ▼
│ PostgreSQL      │                ┌─────────────────────────────────┐
│ (单实例)        │    ────────►   │     PostgreSQL (主从复制)        │
└─────────────────┘                │     + PgBouncer 连接池          │
        │                          └─────────────────────────────────┘
        ▼                                         │
┌─────────────────┐                               ▼
│ Qdrant (单实例) │    ────────►   ┌─────────────────────────────────┐
└─────────────────┘                │     Qdrant Cluster (分片)        │
                                   │     + 副本 + 负载均衡            │
                                   └─────────────────────────────────┘
```

#### 扩展策略

| 组件 | 扩展方式 | 触发条件 |
|------|----------|----------|
| Backend | 水平扩展 (增加实例) | CPU > 70% 或 并发 > 100 |
| PostgreSQL | 读写分离 + 连接池 | 连接数 > 100 或 QPS > 1000 |
| Qdrant | 分片 + 副本 | 向量数 > 1000w 或 QPS > 500 |
| Celery Worker | 水平扩展 | 队列积压 > 100 任务 |
| Redis | 集群模式 | 内存 > 80% 或 连接数 > 5000 |

---

## 附录

### A. 部署依赖关系

```
├─ PostgreSQL (数据存储)
│  └─ 用户、项目、进度、分析文档
├─ Redis (缓存 & 队列)
│  └─ 会话、LLM 缓存、Celery Broker
├─ Qdrant (向量存储)
│  └─ 代码向量、文档向量
├─ MinIO (对象存储)
│  └─ 仓库文件、导出文档
├─ Backend (FastAPI + DeepAgents)
│  └─ API 服务、Agent 运行时、Middleware Stack
├─ Celery Worker (异步任务)
│  └─ 代码索引、文档生成
└─ Frontend (可选)
   └─ React/Vue Web 应用
```

### B. 环境变量清单

| 变量名 | 说明 | 示例值 | 必填 |
|--------|------|--------|------|
| `DATABASE__URL` | PostgreSQL 连接串 | `postgresql://user:pass@localhost:5432/db` | 是 |
| `REDIS__URL` | Redis 连接串 | `redis://localhost:6379/0` | 是 |
| `QDRANT__URL` | Qdrant 服务地址 | `http://localhost:6333` | 是 |
| `MINIO__ENDPOINT` | MinIO 端点 | `localhost:9000` | 是 |
| `MINIO__ACCESS_KEY` | MinIO 访问密钥 | - | 是 |
| `MINIO__SECRET_KEY` | MinIO 秘密密钥 | - | 是 |
| `SECRET_KEY` | 应用密钥 | `[随机字符串]` | 是 |
| `OPENAI__API_KEY` | OpenAI API Key | `sk-...` | 是 |
| `OPENAI__MODEL` | 默认模型 | `gpt-4-turbo` | 否 |
| `ANTHROPIC__API_KEY` | Claude API Key | `sk-ant-...` | 否 |
| `CELERY__BROKER_URL` | Celery Broker | `redis://localhost:6379/1` | 是 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 |

### C. 数据模型设计 (ER 图)

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │    projects     │       │    sessions     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │───┐   │ id (PK)         │───┐   │ id (PK)         │
│ email           │   │   │ user_id (FK)    │◄──┘   │ project_id (FK) │◄──┐
│ name            │   │   │ repo_url        │       │ user_id (FK)    │   │
│ created_at      │   │   │ archetype       │       │ learning_mode   │   │
│ settings (JSON) │   │   │ profile (JSON)  │       │ status          │   │
└─────────────────┘   │   │ repo_map (JSON) │       │ progress (JSON) │   │
                      │   │ status          │       │ created_at      │   │
                      │   │ created_at      │       └─────────────────┘   │
                      │   └─────────────────┘                             │
                      │                                                   │
                      │   ┌─────────────────┐       ┌─────────────────┐   │
                      │   │   questions     │       │learning_records │   │
                      │   ├─────────────────┤       ├─────────────────┤   │
                      │   │ id (PK)         │───┐   │ id (PK)         │   │
                      │   │ project_id (FK) │   │   │ session_id (FK) │◄──┘
                      │   │ stage           │   │   │ question_id(FK) │◄──┘
                      │   │ title           │   │   │ user_answer     │
                      │   │ description     │   │   │ evaluation(JSON)│
                      │   │ template_id     │   │   │ time_spent      │
                      │   │ metadata (JSON) │   │   │ created_at      │
                      │   └─────────────────┘   │   └─────────────────┘
                      │                         │
                      │   ┌─────────────────┐   │   ┌─────────────────┐
                      └──►│   analysis      │   │   │     notes       │
                          ├─────────────────┤   │   ├─────────────────┤
                          │ id (PK)         │   │   │ id (PK)         │
                          │ project_id (FK) │   │   │ session_id (FK) │
                          │ section_id      │   └──►│ question_id(FK) │
                          │ content (TEXT)  │       │ content (TEXT)  │
                          │ version         │       │ created_at      │
                          │ created_at      │       │ updated_at      │
                          └─────────────────┘       └─────────────────┘
```

### D. API 接口清单

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v1/projects` | 创建项目 |
| GET | `/api/v1/projects/{id}` | 获取项目详情 |
| GET | `/api/v1/projects/{id}/status` | 获取分析状态 |
| POST | `/api/v1/sessions` | 创建学习会话 |
| GET | `/api/v1/sessions/{id}` | 获取会话详情 |
| GET | `/api/v1/sessions/{id}/questions` | 获取问题列表 |
| POST | `/api/v1/sessions/{id}/answers` | 提交回答 |
| GET | `/api/v1/sessions/{id}/progress` | 获取学习进度 |
| GET | `/api/v1/analysis/{project_id}` | 获取分析文档 |
| GET | `/api/v1/analysis/{project_id}/export` | 导出分析文档 |
| WS | `/ws/agents/{session_id}` | Agent 实时对话 |

### E. 参考资料

#### Agent 框架
- [DeepAgents Documentation](https://github.com/langchain-ai/deepagents) - 主要 Agent 框架
- [DeepAgents Quickstarts](https://github.com/langchain-ai/deepagents-quickstarts) - 示例代码
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) - 底层状态图引擎

#### LangChain 生态 (LLM/向量库封装)
- [LangChain Documentation](https://python.langchain.com/docs/) - LangChain 官方文档
- [LangChain Expression Language (LCEL)](https://python.langchain.com/docs/concepts/lcel/) - 链式编排
- [LangChain Chat Models](https://python.langchain.com/docs/integrations/chat/) - 支持的 LLM 列表
- [LangChain Vector Stores](https://python.langchain.com/docs/integrations/vectorstores/) - 支持的向量库
- [LangChain RAG Best Practices](https://python.langchain.com/docs/tutorials/rag/) - RAG 最佳实践
- [LangChain Prompt Templates](https://python.langchain.com/docs/concepts/prompt_templates/) - Prompt 模版

#### 其他技术
- [tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/) - 代码 AST 解析
- [Qdrant Vector Database](https://qdrant.tech/documentation/) - 向量数据库
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Web 框架
- [Socratic Tutoring in Programming Education](https://dl.acm.org/doi/10.1145/3545945.3569759) - 苏格拉底教学法

---

*本文档最后更新：2025-12-10 (v1.1 - 更新为 DeepAgents 架构)*

