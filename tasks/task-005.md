# TASK-005: 代码索引与向量存储

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-005 |
| **任务名称** | 代码索引与向量存储 |
| **版本** | V0.2 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 3-4 天 |
| **前置任务** | TASK-003, TASK-004 |

---

## 任务描述

实现代码片段的向量化索引服务，将代码按函数/类粒度切分并存储到向量数据库，支持语义搜索。这是 RAG 系统的核心能力。

### 主要工作内容

1. **代码切分器 (`infrastructure/code_analysis/code_splitter.py`)**
   - 按函数/方法切分：每个函数作为一个 chunk
   - 按类切分：每个类（含方法）作为一个 chunk
   - 按文件切分：小文件整体作为一个 chunk
   - 保留上下文：包含导入语句和类定义头
   - 元数据记录：file_path, start_line, end_line, symbol_name

2. **代码索引器 (`infrastructure/code_analysis/code_indexer.py`)**
   - 项目索引：遍历项目所有代码文件
   - 增量索引：只索引变更文件
   - 批量向量化：使用 LangChain OpenAI Embeddings
   - 存储到向量库：使用 TASK-003 的 Qdrant VectorStore
   - 元数据过滤：支持按文件路径、符号类型过滤

3. **向量集合管理**
   - 集合命名：`code_{project_id}`
   - 集合创建：首次索引时自动创建
   - 集合删除：项目删除时清理
   - 集合更新：支持增量更新

4. **语义搜索服务 (`infrastructure/code_analysis/semantic_search.py`)**
   - 代码搜索：根据自然语言查询搜索相关代码
   - 混合搜索：语义 + 关键词
   - 结果排序：相关度排序
   - 结果去重：相同文件的多个 chunk 合并

5. **Celery 索引任务**
   - 全量索引任务：新项目首次索引
   - 增量索引任务：代码更新后重新索引
   - 进度上报：索引进度百分比

---

## 验收标准

- [ ] 代码切分保持语义完整性（函数/类不被截断）
- [ ] 每个 chunk 包含完整元数据（文件路径、行号、符号名）
- [ ] 索引 1000 个文件耗时 < 5 分钟
- [ ] 向量搜索延迟 < 500ms (top 10)
- [ ] 支持按文件路径过滤搜索结果
- [ ] 搜索结果包含代码片段和位置信息
- [ ] 项目删除时向量集合同步删除
- [ ] 支持增量索引，只处理变更文件
- [ ] 提供索引状态查询 API

---

## 注意事项

1. **切分策略**
   - 代码优先按语法结构切分，而非固定长度
   - 保留必要的上下文（imports、class 定义）
   - 过长的函数考虑进一步切分

2. **向量维度**
   - OpenAI text-embedding-3-small: 1536 维
   - Qdrant 集合需指定正确维度

3. **元数据设计**
   ```python
   metadata = {
       "project_id": "proj_xxx",
       "file_path": "src/main.py",
       "start_line": 10,
       "end_line": 25,
       "symbol_name": "MyClass.my_method",
       "symbol_type": "method",
       "language": "python"
   }
   ```

4. **性能优化**
   - 批量向量化：每批 100 个 chunk
   - 并发写入向量库
   - 大项目分批处理，避免内存溢出

5. **错误处理**
   - 单文件解析失败不影响整体索引
   - 记录失败文件列表
   - 支持重试失败的文件

---

## 相关文档

- [架构设计文档 - 5.2 代码索引数据流](../docs/code-learning-coach-architecture.md#52-代码索引数据流)
- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
