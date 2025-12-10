# TASK-007: 领域服务与仓储实现

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-007 |
| **任务名称** | 领域服务与仓储实现 |
| **版本** | V0.3 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 3-4 天 |
| **前置任务** | TASK-002, TASK-006 |

---

## 任务描述

实现领域层的仓储接口，以及基础设施层的仓储实现。同时实现工作单元模式 (Unit of Work) 管理事务。

### 主要工作内容

1. **仓储接口定义 (`domain/repositories/`)**
   - **IProjectRepository**
     - `get_by_id(id) -> Project`
     - `list_all() -> List[Project]`
     - `save(project) -> None`
     - `delete(id) -> None`
   
   - **ISessionRepository**
     - `get_by_id(id) -> LearningSession`
     - `get_by_project(project_id) -> List[LearningSession]`
     - `save(session) -> None`
   
   - **IQuestionRepository**
     - `get_by_id(id) -> Question`
     - `get_by_project(project_id) -> List[Question]`
     - `get_by_stage(project_id, stage) -> List[Question]`
     - `save_batch(questions) -> None`
   
   - **IAnalysisRepository**
     - `get_by_project(project_id) -> Analysis`
     - `get_section(project_id, section_id) -> Section`
     - `save(analysis) -> None`
   
   - **ILearningRecordRepository**
     - `get_by_session(session_id) -> List[LearningRecord]`
     - `get_by_question(session_id, question_id) -> LearningRecord`
     - `save(record) -> None`

2. **仓储实现 (`infrastructure/repositories/`)**
   - PostgreSQL 实现所有仓储接口
   - 使用 SQLAlchemy 2.0 异步 API
   - ORM 模型与领域实体相互转换
   - 支持批量操作优化

3. **工作单元模式 (`infrastructure/unit_of_work.py`)**
   - 管理数据库事务
   - 提供所有仓储的访问入口
   - 支持 async context manager
   - 支持事务回滚

4. **领域服务实现 (`domain/services/`)**
   - **CodeAnalyzer**: 代码分析服务（接口在领域层，实现在基础设施层）
   - **QuestionGenerator**: 问题生成服务
   - **ProgressTracker**: 进度跟踪服务

---

## 验收标准

- [ ] 所有仓储接口定义在 `domain/repositories/`
- [ ] 所有仓储实现在 `infrastructure/repositories/`
- [ ] 仓储使用 SQLAlchemy 2.0 异步 API
- [ ] Unit of Work 支持事务管理
- [ ] 支持 `async with uow:` 上下文管理
- [ ] ORM 模型到领域实体的转换正确
- [ ] 批量操作使用 `bulk_insert_mappings` 优化
- [ ] 单元测试覆盖仓储的 CRUD 操作
- [ ] 测试使用内存数据库或 Mock

---

## 注意事项

1. **仓储模式原则**
   ```python
   # 仓储接口在领域层
   # domain/repositories/project_repository.py
   class IProjectRepository(ABC):
       @abstractmethod
       async def get_by_id(self, id: str) -> Optional[Project]:
           pass
   
   # 仓储实现在基础设施层
   # infrastructure/repositories/postgres_project_repo.py
   class PostgresProjectRepository(IProjectRepository):
       async def get_by_id(self, id: str) -> Optional[Project]:
           async with self.session() as session:
               model = await session.get(ProjectModel, id)
               return self._to_entity(model) if model else None
   ```

2. **工作单元使用**
   ```python
   async with UnitOfWork() as uow:
       project = await uow.projects.get_by_id(project_id)
       project.start_analysis()
       await uow.projects.save(project)
       await uow.commit()
   ```

3. **实体与模型转换**
   - 仓储负责 ORM 模型 <-> 领域实体 转换
   - 转换逻辑在仓储内部，不暴露给外部
   - JSON 字段需要正确序列化/反序列化

4. **性能优化**
   - 使用 `selectinload` 预加载关联数据
   - 批量查询避免 N+1 问题
   - 合理使用索引

5. **异步注意事项**
   - 使用 `async_sessionmaker`
   - 避免在异步上下文中使用同步 ORM 操作
   - 注意会话生命周期管理

---

## 相关文档

- [架构设计文档 - 2.2 各层职责说明](../docs/code-learning-coach-architecture.md#22-各层职责说明)
- [SQLAlchemy 2.0 异步文档](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
