# TASK-001: 项目结构初始化与配置管理

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-001 |
| **任务名称** | 项目结构初始化与配置管理 |
| **版本** | V0.1 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 2-3 天 |
| **前置任务** | 无 |

---

## 任务描述

基于 DDD 分层架构，初始化「开源项目学习教练 AI 智能体」的项目目录结构，配置环境变量管理、日志系统、异常处理等基础设施。确保项目符合 AGENTS.md 中定义的代码规范。

### 主要工作内容

1. **目录结构调整**
   - 创建 `application/agents/` 目录用于 DeepAgents 编排
   - 创建 `application/agents/subagents/` 存放子 Agent 定义
   - 创建 `application/agents/middleware/` 存放自定义中间件
   - 创建 `infrastructure/langchain/` 存放 LangChain 封装
   - 创建 `infrastructure/code_analysis/` 存放代码分析服务
   - 创建 `templates/questions/` 存放问题模版
   - 创建 `templates/analysis/` 存放分析文档模版

2. **配置管理扩展**
   - 扩展 `core/config.py` 添加 LLM、Embedding、VectorStore 配置
   - 仅保留 OpenAI Chat/Embedding 配置
   - 仅保留 Qdrant 向量库配置
   - 添加 MinIO 对象存储配置

3. **环境变量定义**
   - 更新 `env.example` 包含所有必需环境变量
   - 添加 OpenAI API Key 配置项
   - 添加 Qdrant 向量数据库连接配置
   - 添加对象存储配置

4. **依赖管理**
   - 更新 `requirements.txt` 添加 LangChain v1.x 相关包
   - 保留 DeepAgents / LangGraph 依赖
   - 添加 tree-sitter 依赖
   - 添加 qdrant-client 依赖

---

## 验收标准

- [ ] 目录结构符合架构文档 2.3 节定义
- [ ] `core/config.py` 包含所有 LLM/Embedding/VectorStore 配置类
- [ ] 配置支持从环境变量读取，遵循 `SECTION__KEY` 命名规范
- [ ] `env.example` 包含所有配置项及说明注释
- [ ] `requirements.txt` 包含所有依赖且版本号明确
- [ ] 运行 `pip install -r requirements.txt` 无错误
- [ ] 配置缺失时应用启动报错并给出明确提示
- [ ] 日志配置支持 structlog 结构化输出

---

## 注意事项

1. **配置命名规范**
   - 环境变量使用双下划线分隔层级：`DATABASE__URL`、`OPENAI__API_KEY`
   - Pydantic Settings 自动解析嵌套配置

2. **敏感信息处理**
   - API Key 等敏感信息不得硬编码
   - `env.example` 中使用占位符，不包含真实密钥
   - 配置类中敏感字段使用 `SecretStr` 类型

3. **向后兼容**
   - 保留现有 `file_asset` 相关代码结构
   - 新增目录不影响现有功能

4. **LangChain 版本**
   - 使用 LangChain v1.x 版本
   - langchain-core、langchain-openai、langchain-qdrant 等需版本对齐

---

## 相关文档

- [架构设计文档 - 2.3 目录结构](../docs/code-learning-coach-architecture.md#23-目录结构)
- [架构设计文档 - 附录B 环境变量清单](../docs/code-learning-coach-architecture.md#b-环境变量清单)
