# TASK-006: 领域实体与值对象

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-006 |
| **任务名称** | 领域实体与值对象 |
| **版本** | V0.3 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 2-3 天 |
| **前置任务** | TASK-002 |

---

## 任务描述

实现领域层的核心实体和值对象，采用充血模型设计，包含业务逻辑和领域事件。遵循 DDD 原则，领域层不依赖任何基础设施。

### 主要工作内容

1. **实体定义 (`domain/entities/`)**
   - **Project 实体**：项目聚合根，包含项目生命周期管理
   - **LearningSession 实体**：学习会话，包含会话状态机
   - **Question 实体**：问题，包含问题状态和评估逻辑
   - **Analysis 实体**：分析文档，包含章节管理
   - **Note 实体**：学习笔记，包含版本管理
   - **LearningProgress 实体**：会话进度，包含统计计算

2. **值对象定义 (`domain/value_objects/`)**
   - **ProjectProfile**：项目画像，包含语言、框架、依赖等
   - **RepoMap**：代码地图，包含模块、核心类、调用关系
   - **QuestionGraph**：问题依赖图，节点和边
   - **CapabilityModule**：能力模块定义
   - **Evaluation**：回答评估结果
   - **Explanation**：代码讲解内容

3. **领域枚举**
   - **ProjectStatus**：PENDING, PROCESSING, READY, FAILED
   - **SessionStatus**：ACTIVE, PAUSED, COMPLETED
   - **LearningMode**：MACRO, CAPABILITY
   - **QuestionStage**：ARCHITECTURE, MODULE, CLASS, METHOD, DESIGN
   - **Archetype**：WEB_BACKEND, LIBRARY, AGENT_FRAMEWORK, RAG_SYSTEM, FRONTEND_SPA

4. **领域事件 (`domain/events/`)**
   - ProjectCreated, ProjectAnalyzed, ProjectFailed
   - SessionStarted, SessionPaused, SessionCompleted
   - QuestionAnswered, QuestionSkipped
   - AnalysisGenerated, NoteCreated

5. **领域服务接口 (`domain/services/`)**
   - ICodeAnalyzer：代码分析接口
   - IQuestionGenerator：问题生成接口
   - IProgressTracker：进度跟踪接口

---

## 验收标准

- [ ] 所有实体继承自 `domain/common/entity.py` 的 Entity 基类
- [ ] 所有值对象继承自 `domain/common/value_object.py` 的 ValueObject 基类
- [ ] 值对象实现 `__eq__` 和 `__hash__` 方法
- [ ] 实体包含业务方法，不仅仅是数据容器
- [ ] 领域层无任何 infrastructure 导入
- [ ] 领域事件使用 Pydantic 定义，支持序列化
- [ ] 枚举使用 Python Enum 或 StrEnum
- [ ] 提供完整的类型提示
- [ ] 单元测试覆盖实体的核心业务方法

---

## 注意事项

1. **充血模型原则**
   ```python
   # 正确：实体包含业务逻辑
   class Project(Entity):
       def start_analysis(self):
           if self.status != ProjectStatus.PENDING:
               raise InvalidStateError("项目不在待处理状态")
           self.status = ProjectStatus.PROCESSING
           self.add_event(ProjectAnalysisStarted(self.id))
   
   # 错误：贫血模型，只有数据
   class Project(Entity):
       status: ProjectStatus  # 仅数据字段
   ```

2. **值对象不可变**
   ```python
   @dataclass(frozen=True)
   class ProjectProfile:
       archetype: str
       language: str
       framework: str
   ```

3. **聚合边界**
   - Project 是聚合根，包含 ProjectProfile, RepoMap
   - LearningSession 是聚合根，包含进度数据
   - Question 可独立存在，关联到 Project

4. **领域事件设计**
   - 事件名使用过去式：ProjectCreated, AnalysisCompleted
   - 事件包含必要的上下文数据
   - 事件支持 JSON 序列化

5. **依赖反转**
   - 领域服务定义接口（ICodeAnalyzer）
   - 基础设施层实现接口
   - 通过依赖注入传递实现

---

## 相关文档

- [架构设计文档 - 2.1 分层架构图](../docs/code-learning-coach-architecture.md#21-分层架构图-ddd-风格--deepagents)
- [架构设计文档 - 领域层说明](../docs/code-learning-coach-architecture.md#22-各层职责说明)
