# TASK-014: 应用服务层实现

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-014 |
| **任务名称** | 应用服务层实现 |
| **版本** | V0.5 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 3-4 天 |
| **前置任务** | TASK-007, TASK-011 |

---

## 任务描述

实现应用层服务，作为 API 层和领域层之间的协调者。负责用例编排、事务管理、DTO 转换、Agent 调用等职责。

### 主要工作内容

1. **项目服务 (`application/services/project_service.py`)**
   
   **方法：**
   - `create_project(repo_url, goals, capabilities) -> ProjectDTO`
     - 验证仓库 URL
     - 创建 Project 实体
     - 触发异步分析任务
     - 返回项目 DTO
   
   - `get_project(project_id) -> ProjectDTO`
   - `list_projects(page, page_size) -> List[ProjectDTO]`
   - `delete_project(project_id) -> None`
   - `get_project_status(project_id) -> ProjectStatusDTO`
   - `get_project_profile(project_id) -> ProjectProfileDTO`
   - `get_repo_map(project_id) -> RepoMapDTO`

2. **会话服务 (`application/services/session_service.py`)**
   
   **方法：**
   - `create_session(project_id, mode, capabilities) -> SessionDTO`
     - 检查项目状态
     - 调用 Question Planner
     - 调用 Analysis Generator
     - 创建 Session 实体
   
   - `get_session(session_id) -> SessionDTO`
   - `pause_session(session_id) -> SessionDTO`
   - `resume_session(session_id) -> SessionDTO`
   - `complete_session(session_id) -> SessionDTO`
   - `get_progress(session_id) -> ProgressDTO`

3. **学习服务 (`application/services/learning_service.py`)**
   
   **方法：**
   - `get_current_question(session_id) -> QuestionDTO`
   - `submit_answer(session_id, question_id, answer) -> FeedbackDTO`
     - 调用 Tutor Agent 评估
     - 调用 Explainer Agent 讲解
     - 记录学习记录
     - 更新进度
   
   - `skip_question(session_id, question_id) -> QuestionDTO`
   - `get_question_history(session_id) -> List[LearningRecordDTO]`

4. **分析服务 (`application/services/analysis_service.py`)**
   
   **方法：**
   - `get_analysis(project_id) -> AnalysisDTO`
   - `get_section(project_id, section_id) -> SectionDTO`
   - `regenerate_section(project_id, section_id) -> SectionDTO`
   - `export_analysis(project_id, format) -> str`

5. **DTO 定义 (`application/dtos/`)**
   - ProjectDTO, ProjectProfileDTO, RepoMapDTO
   - SessionDTO, ProgressDTO
   - QuestionDTO, FeedbackDTO, LearningRecordDTO
   - AnalysisDTO, SectionDTO
   - NoteDTO

---

## 验收标准

- [ ] 所有服务方法使用 Unit of Work 管理事务
- [ ] 服务层不直接访问数据库，通过仓储
- [ ] DTO 使用 Pydantic 定义，支持序列化
- [ ] Agent 调用异步执行
- [ ] 服务方法包含完整的参数验证
- [ ] 业务异常转换为领域异常
- [ ] 服务方法有完整的日志记录
- [ ] 单元测试覆盖核心业务流程

---

## 注意事项

1. **服务层职责**
   ```python
   class ProjectService:
       def __init__(
           self,
           uow: IUnitOfWork,
           coach_agent: LearningCoachAgent,
       ):
           self.uow = uow
           self.agent = coach_agent
       
       async def create_project(
           self,
           repo_url: str,
           goals: List[str],
       ) -> ProjectDTO:
           # 1. 验证输入
           self._validate_repo_url(repo_url)
           
           # 2. 创建实体
           project = Project.create(repo_url, goals)
           
           # 3. 持久化
           async with self.uow:
               await self.uow.projects.save(project)
               await self.uow.commit()
           
           # 4. 触发异步分析
           await self._trigger_analysis(project.id)
           
           # 5. 转换 DTO
           return ProjectDTO.from_entity(project)
   ```

2. **DTO 转换**
   ```python
   class ProjectDTO(BaseModel):
       id: str
       repo_url: str
       name: str
       status: str
       created_at: datetime
       
       @classmethod
       def from_entity(cls, entity: Project) -> "ProjectDTO":
           return cls(
               id=entity.id,
               repo_url=entity.repo_url,
               name=entity.name,
               status=entity.status.value,
               created_at=entity.created_at,
           )
   ```

3. **事务边界**
   - 每个服务方法是一个事务边界
   - 使用 `async with uow:` 管理事务
   - 异常时自动回滚

4. **Agent 调用**
   - 使用依赖注入获取 Agent 实例
   - Agent 调用可能耗时，考虑超时处理
   - Agent 失败时记录错误并返回友好信息

5. **日志规范**
   - 入口记录：方法调用参数
   - 出口记录：返回结果摘要
   - 异常记录：完整堆栈

---

## 相关文档

- [架构设计文档 - 2.2 各层职责说明](../docs/code-learning-coach-architecture.md#22-各层职责说明)
- [架构设计文档 - 4. 核心通信流程](../docs/code-learning-coach-architecture.md#4-核心通信流程)
