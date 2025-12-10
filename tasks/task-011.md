# TASK-011: DeepAgents 主 Agent 编排

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-011 |
| **任务名称** | DeepAgents 主 Agent 编排 |
| **版本** | V0.4 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 3-4 天 |
| **前置任务** | TASK-008, TASK-009, TASK-010 |

---

## 任务描述

使用 DeepAgents 框架创建主 Agent (Learning Coach)，整合所有子 Agent，配置中间件栈，实现完整的学习教练智能体编排。

### 主要工作内容

1. **主 Agent 定义 (`application/agents/coach_agent.py`)**
   
   **配置内容：**
   - 系统提示词 (System Prompt)
   - 子 Agent 列表 (SubAgents)
   - 中间件栈 (Middleware Stack)
   - 工具定义 (Tools)
   - 中断点配置 (Interrupt Points)

2. **中间件配置**
   
   **内置中间件：**
   - `TodoListMiddleware`：任务规划和进度跟踪
   - `FilesystemMiddleware`：笔记存储和进度持久化
   - `SubAgentMiddleware`：子 Agent 调度
   - `SummarizationMiddleware`：大仓库上下文摘要
   
   **自定义中间件：**
   - `ProgressMiddleware`：学习进度跟踪
   - `RAGMiddleware`：RAG 检索增强

3. **子 Agent 集成**
   ```python
   learning_coach = create_deep_agent(
       model=ChatOpenAI(model="gpt-4-turbo"),
       system_prompt="你是开源项目学习教练...",
       subagents=[
           profiler_subagent,
           mapper_subagent,
           planner_subagent,
           generator_subagent,
           tutor_subagent,
           explainer_subagent,
       ],
       interrupt_on=["complete_learning_session"],
   )
   ```

4. **工作流定义**
   
   **项目分析流程：**
   1. 接收仓库 URL
   2. `task("project-profiler", ...)` 生成 ProjectProfile
   3. `task("repo-mapper", ...)` 生成 RepoMap
   4. `task("question-planner", ...)` 生成 QuestionGraph
   5. `task("analysis-generator", ...)` 生成分析文档
   
   **学习循环流程：**
   1. 选择当前问题
   2. 展示当前问题
   3. 提交回答
   4. `task("tutor", ...)` 评估回答
   5. `task("explainer", ...)` 生成讲解
   6. 记录学习进度
   7. 循环到下一题

5. **状态管理**
   - 项目状态：ProjectProfile, RepoMap
   - 会话状态：当前问题、进度、已完成问题
   - 对话历史：消息列表

---

## 验收标准

- [ ] 主 Agent 能正确调度所有子 Agent
- [ ] `task()` 工具能正确委托任务到子 Agent
- [ ] 子 Agent 上下文隔离，不污染主 Agent
- [ ] 中间件按正确顺序执行
- [ ] TodoListMiddleware 正确跟踪任务进度
- [ ] FilesystemMiddleware 正确持久化笔记
- [ ] 支持长时间运行的学习会话
- [ ] 支持会话中断和恢复
- [ ] 提供会话状态查询接口
- [ ] 主 Agent 响应时间 < 30 秒

---

## 注意事项

1. **System Prompt 设计**
   ```markdown
   你是「开源项目学习教练」，帮助开发者深入理解开源项目。
   
   你的能力:
   1. 分析任意代码仓库的架构和设计
   2. 生成个性化的学习问题序列
   3. 通过苏格拉底式问答引导学习
   4. 基于代码检索提供准确讲解
   
   工作流程:
   1. 接收仓库 URL 和学习目标
   2. 委托 project-profiler 分析项目
   3. 委托 repo-mapper 构建代码地图
   ...
   
   重要: 使用 write_todos 规划任务，使用 task() 委托子 Agent
   ```

2. **中间件顺序**
   - TodoListMiddleware 在最外层
   - SubAgentMiddleware 在内层
   - 自定义中间件根据需要插入

3. **错误处理**
   - 子 Agent 失败不应导致主 Agent 崩溃
   - 提供降级策略
   - 记录详细错误日志

4. **状态持久化**
   - 使用 LangGraph 检查点功能
   - 或使用 Redis 存储会话状态
   - 支持服务器重启后恢复

5. **性能优化**
   - 并行执行独立的子任务
   - 缓存常用的分析结果
   - 流式输出减少等待时间

---

## 相关文档

- [架构设计文档 - 7.4 DeepAgents 主 Agent 设计](../docs/code-learning-coach-architecture.md#74-deepagents-主-agent-设计)
- [架构设计文档 - 1.4 DeepAgents 中间件架构](../docs/code-learning-coach-architecture.md#14-deepagents-中间件架构)
- [DeepAgents 文档](https://github.com/langchain-ai/deepagents)
