# TASK-008: Project Profiler 与 Repo Mapper 子 Agent

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-008 |
| **任务名称** | Project Profiler 与 Repo Mapper 子 Agent |
| **版本** | V0.4 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 4-5 天 |
| **前置任务** | TASK-003, TASK-004, TASK-005 |

---

## 任务描述

实现项目画像器 (Project Profiler) 和代码地图生成器 (Repo Mapper) 两个子 Agent，作为项目分析的核心组件。使用 DeepAgents 的 SubAgent 机制实现。

### 主要工作内容

1. **Project Profiler SubAgent (`application/agents/subagents/profiler_agent.py`)**
   
   **职责：**
   - 克隆/加载仓库
   - 分析编程语言和比例
   - 识别主要框架和依赖
   - 识别项目原型 (archetype)
   - 扫描目录结构，识别各层职责
   - 提取配置文件内容
   
   **工具定义：**
   - `clone_repository(repo_url: str) -> dict`：克隆仓库
   - `scan_directory(path: str) -> dict`：扫描目录结构
   - `detect_language(path: str) -> dict`：检测语言比例
   - `parse_config(file_path: str) -> dict`：解析配置文件
   
   **输出：**
   - `ProjectProfile` 值对象 (JSON)

2. **Repo Mapper SubAgent (`application/agents/subagents/mapper_agent.py`)**
   
   **职责：**
   - 构建模块列表和关系
   - 解析 AST 提取符号
   - 识别核心类和关键方法
   - 构建调用关系图
   - 识别能力模块候选
   
   **工具定义：**
   - `parse_file(file_path: str) -> dict`：解析单文件 AST
   - `extract_symbols(path: str) -> list`：提取符号列表
   - `build_call_graph(symbols: list) -> dict`：构建调用图
   - `identify_capabilities(repo_map: dict) -> list`：识别能力模块
   
   **输出：**
   - `RepoMap` 值对象 (JSON)
   - `CapabilityCandidates` 列表

3. **Archetype 识别逻辑**
   - `web_backend`：检测 FastAPI/Django/Flask/Express
   - `library`：检测 setup.py/pyproject.toml 发布配置
   - `agent_framework`：检测 LangGraph/AutoGen/CrewAI
   - `rag_system`：检测向量库和 Embedding 使用
   - `frontend_spa`：检测 React/Vue/Angular

4. **能力模块识别逻辑**
   - 目录命名：`plugins/`, `auth/`, `cache/`, `workflow/`
   - 框架特征：middleware 管道、事件总线
   - 依赖特征：redis (缓存)、celery (任务队列)

---

## 验收标准

- [ ] Profiler 能正确识别 Python/TypeScript/Java/Go 项目
- [ ] Profiler 能正确识别 FastAPI/Django/Express/Spring 框架
- [ ] Profiler 生成的 ProjectProfile 包含所有必需字段
- [ ] Mapper 能正确提取 Python 类和函数符号
- [ ] Mapper 能正确提取 TypeScript 接口和函数符号
- [ ] Mapper 能识别至少 3 种能力模块类型
- [ ] 子 Agent 使用 DeepAgents SubAgent 定义
- [ ] 子 Agent 工具定义符合 `@tool` 装饰器规范
- [ ] 分析中等大小项目 (1000 文件) 耗时 < 3 分钟
- [ ] 提供分析结果示例和测试用例

---

## 注意事项

1. **SubAgent 定义示例**
   ```python
   from deepagents import SubAgent
   from deepagents.tools import tool
   
   @tool
   def clone_repository(repo_url: str) -> dict:
       """克隆 Git 仓库到本地工作空间"""
       # 调用 GitService
       pass
   
   profiler_subagent = SubAgent(
       name="project-profiler",
       description="分析项目结构、识别语言框架、生成项目画像",
       system_prompt="你是项目分析专家...",
       tools=[clone_repository, scan_directory, detect_language],
   )
   ```

2. **Archetype 优先级**
   - 同时匹配多个时，按特殊性排序
   - `agent_framework` > `rag_system` > `web_backend` > `library`

3. **大项目处理**
   - 设置文件数量上限 (10000)
   - 设置单文件大小上限 (1MB)
   - 跳过 node_modules、vendor 等目录
   - 跳过二进制文件和图片

4. **错误处理**
   - 解析失败的文件记录日志但不中断
   - 返回部分结果而非完全失败
   - 标记分析完整度

5. **缓存策略**
   - 相同仓库 URL 的分析结果可缓存
   - 缓存有效期 24 小时
   - 强制刷新参数

---

## 相关文档

- [架构设计文档 - 6.1 Project Profiler](../docs/code-learning-coach-architecture.md#61-project-profiler项目画像器)
- [架构设计文档 - 6.2 Repo Mapper](../docs/code-learning-coach-architecture.md#62-repo-mapper代码地图生成器)
- [PRD - 3.2 关键子智能体](../docs/es%20install.md)

