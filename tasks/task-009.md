# TASK-009: Question Planner 与 Analysis Generator 子 Agent

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-009 |
| **任务名称** | Question Planner 与 Analysis Generator 子 Agent |
| **版本** | V0.4 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 4-5 天 |
| **前置任务** | TASK-006, TASK-008 |

---

## 任务描述

实现问题规划器 (Question Planner) 和分析文档生成器 (Analysis Generator) 两个子 Agent。Question Planner 负责生成个性化的问题序列，Analysis Generator 负责生成九大章节的分析文档。

### 主要工作内容

1. **问题模版库 (`templates/questions/`)**
   
   **按 Archetype 分类：**
   - `web_backend/`：Web 后端项目问题模版
   - `agent_framework/`：Agent 框架项目问题模版
   - `library/`：库项目问题模版
   - `frontend_spa/`：前端 SPA 项目问题模版
   - `rag_system/`：RAG 系统项目问题模版
   
   **模版结构 (YAML)：**
   ```yaml
   id: arch_001
   archetype: agent_framework
   stage: 整体架构分析
   difficulty: medium
   title_template: "项目的 {module_name} 模块是如何设计的？"
   description_template: |
     请分析 {project_name} 中 {module_name} 的设计...
   placeholders: [project_name, module_name, entry_file]
   recommended_files: ["{entry_file}", "src/"]
   prerequisites: [arch_000]
   tags: [architecture, design]
   ```

2. **Question Planner SubAgent (`application/agents/subagents/planner_agent.py`)**
   
   **职责：**
   - 加载问题模版库
   - 根据项目 archetype 筛选模版
   - 根据 ProjectProfile 和 RepoMap 实例化问题
   - 构建问题依赖图 (QuestionGraph)
   - 根据选定的能力模块过滤问题
   
   **工具定义：**
   - `load_templates(archetype: str) -> list`：加载模版
   - `instantiate_question(template: dict, context: dict) -> dict`：实例化问题
   - `build_question_graph(questions: list) -> dict`：构建问题图
   - `select_next_question(graph: dict, progress: dict) -> dict`：选择下一题
   
   **输出：**
   - `QuestionGraph` 值对象

3. **Analysis Generator SubAgent (`application/agents/subagents/generator_agent.py`)**
   
   **职责：**
   - 按九大章节模版生成分析文档
   - 基于代码检索 (RAG) 生成内容
   - 引用具体代码位置
   - 支持增量生成单个章节
   
   **九大章节：**
   1. 整体架构分析
   2. 各模块职责与内部关系
   3. 核心类解剖
   4. 关键方法深度解析
   5. 模块间调用依赖关系分析
   6. 核心流程分析
   7. 核心入口 & 主要数据流
   8. 设计亮点与精妙之处
   9. 从源码看最佳实践
   
   **工具定义：**
   - `search_code(query: str, project_id: str) -> list`：代码检索
   - `generate_section(section_id: str, context: dict) -> str`：生成章节
   - `export_analysis(format: str) -> str`：导出文档

4. **分析模版 (`templates/analysis/nine_sections.md`)**
   - 定义每个章节的结构和要点
   - 提供章节生成的 Prompt 模版

---

## 验收标准

- [ ] 问题模版库包含至少 3 种 archetype，每种至少 10 个模版
- [ ] 问题实例化正确替换占位符
- [ ] QuestionGraph 正确表示问题依赖关系
- [ ] 能力模块过滤后只显示相关问题
- [ ] Analysis Generator 能生成完整的九大章节
- [ ] 生成的分析文档引用真实代码位置
- [ ] 单章节生成耗时 < 30 秒
- [ ] 完整分析文档生成耗时 < 5 分钟
- [ ] 支持导出 Markdown 格式

---

## 注意事项

1. **问题实例化示例**
   ```python
   template = {
       "title_template": "{project_name} 的 Agent 编排如何实现？",
       "placeholders": ["project_name", "entry_file"]
   }
   context = {
       "project_name": "LangGraph",
       "entry_file": "src/graph.py"
   }
   # 输出: "LangGraph 的 Agent 编排如何实现？"
   ```

2. **QuestionGraph 结构**
   ```python
   {
       "nodes": [
           {"id": "q_001", "title": "...", "stage": "架构", "prerequisites": []},
           {"id": "q_002", "title": "...", "stage": "模块", "prerequisites": ["q_001"]}
       ],
       "edges": [
           {"from": "q_001", "to": "q_002"}
       ]
   }
   ```

3. **分析文档质量**
   - 必须基于实际代码，不能编造
   - 引用格式：`文件路径:行号`
   - 代码块使用 markdown 格式

4. **RAG 检索优化**
   - 每个章节使用针对性的查询
   - 检索结果去重
   - 相关度阈值过滤

5. **增量生成**
   - 支持只生成指定章节
   - 支持重新生成单个章节
   - 保存中间状态

---

## 相关文档

- [架构设计文档 - 6.3 Question Planner](../docs/code-learning-coach-architecture.md#63-question-planner问题规划器)
- [架构设计文档 - 6.4 Analysis Generator](../docs/code-learning-coach-architecture.md#64-analysis-generator分析文档生成器)
- [PRD - 四、问题系统设计](../docs/es%20install.md)
- [PRD - 五、分析文档设计](../docs/es%20install.md)
