# TASK-003: LangChain 封装层实现

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-003 |
| **任务名称** | LangChain 封装层实现 |
| **版本** | V0.1 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 3-4 天 |
| **前置任务** | TASK-001 |

---

## 任务描述

实现 LangChain 统一封装层，提供 LLM、Embedding、VectorStore、Retriever 的工厂方法，统一使用 OpenAI LLM/Embedding 与 Qdrant VectorStore（可通过配置调整模型参数）。这是整个智能体系统的基础能力层。

### 主要工作内容

1. **LLM 封装 (`infrastructure/langchain/llm.py`)**
   - 实现 `get_llm()` 工厂方法
   - 支持 OpenAI (ChatOpenAI)
   - 统一返回 `BaseChatModel` 类型
   - 支持温度、最大 token 等参数配置

2. **Embedding 封装 (`infrastructure/langchain/embeddings.py`)**
   - 实现 `get_embeddings()` 工厂方法
   - 支持 OpenAI Embeddings
   - 统一返回 `Embeddings` 类型
   - 支持模型名称、维度配置

3. **VectorStore 封装 (`infrastructure/langchain/vectorstore.py`)**
   - 实现 `get_vectorstore()` 工厂方法
   - 支持 Qdrant
   - 统一返回 `VectorStore` 类型
   - 支持集合名称、过滤条件配置

4. **Retriever 封装 (`infrastructure/langchain/retrievers.py`)**
   - 实现 `get_code_retriever()` 方法
   - 支持 MMR (Maximal Marginal Relevance) 搜索
   - 支持相似度搜索
   - 可选：上下文压缩 Retriever
   - 支持 top_k、fetch_k 参数

5. **Prompt 模版 (`infrastructure/langchain/prompts/`)**
   - 代码讲解 Prompt 模版
   - 问题生成 Prompt 模版
   - Tutor 对话 Prompt 模版
   - 使用 `ChatPromptTemplate` 结构化管理

6. **RAG Chain (`infrastructure/langchain/chains/`)**
   - 实现 `create_code_qa_chain()` 代码问答链
   - 使用 LCEL (LangChain Expression Language)
   - 支持流式输出
   - 支持异步调用

---

## 验收标准

- [ ] `get_llm()` 仅支持 OpenAI provider，配置可切换模型名称
- [ ] `get_embeddings()` 仅支持 OpenAI Embedding provider
- [ ] `get_vectorstore()` 仅支持 Qdrant provider
- [ ] 所有工厂方法通过配置文件读取默认 provider
- [ ] 切换 provider 只需修改配置，无需改代码
- [ ] Prompt 模版支持变量替换
- [ ] RAG Chain 支持异步调用 `await chain.ainvoke()`
- [ ] RAG Chain 支持流式输出 `async for chunk in chain.astream()`
- [ ] 单元测试覆盖所有工厂方法
- [ ] 提供使用示例文档

---

## 注意事项

1. **API Key 安全**
   - 不在代码中硬编码 API Key
   - 使用 `settings.openai.api_key` 读取
   - 日志中不打印 API Key

2. **错误处理**
   - provider 不支持时抛出明确的 ValueError
   - API 调用失败时包装为自定义异常
   - 记录详细的错误日志

3. **性能优化**
   - VectorStore 客户端复用，避免重复创建连接
   - 考虑使用单例模式管理客户端实例
   - Embedding 批量处理时使用 `embed_documents()`

4. **类型提示**
   - 所有公开方法添加完整类型提示
   - 返回类型使用 LangChain 的抽象基类

5. **依赖版本**
   - langchain ^1.0.0 以上 (v1.x)
   - langchain-core 同步到 v1.x
   - langchain-openai ^1.0.0
   - langchain-qdrant ^1.0.0

---

## 相关文档

- [架构设计文档 - 7.4 LangChain 集成架构](../docs/code-learning-coach-architecture.md#74-langchain-集成架构)
- [LangChain 官方文档](https://python.langchain.com/docs/)
