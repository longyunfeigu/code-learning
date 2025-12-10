# TASK-002: 数据库模型与迁移

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-002 |
| **任务名称** | 数据库模型与迁移 |
| **版本** | V0.1 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 2-3 天 |
| **前置任务** | TASK-001 |

---

## 任务描述

设计并实现项目核心数据模型，包括项目、学习会话、问题、分析文档、学习记录、笔记等实体的 ORM 模型定义，并生成对应的 Alembic 数据库迁移脚本。当前目标为无用户概念的单租户场景。

### 主要工作内容

1. **项目模型 (projects)**
   - 项目信息：id, repo_url, name
   - 项目元数据：archetype, primary_language, framework
   - 分析数据：profile (JSON), repo_map (JSON)
   - 状态管理：status (PENDING/PROCESSING/READY/FAILED)
   - 时间戳：created_at, updated_at

2. **学习会话模型 (sessions)**
   - 会话信息：id, project_id
   - 学习模式：learning_mode (macro/capability)
   - 进度数据：progress (JSON), current_stage
   - 选中的能力模块：selected_capabilities (JSON)
   - 状态：status (ACTIVE/PAUSED/COMPLETED)

3. **问题模型 (questions)**
   - 问题信息：id, project_id, template_id
   - 问题内容：title, description, stage
   - 元数据：difficulty, recommended_files (JSON)
   - 依赖关系：prerequisites (JSON)
   - 标签：tags (JSON)

4. **学习记录模型 (learning_records)**
   - 记录信息：id, session_id, question_id
   - 回答内容：answer (TEXT)
   - 评估结果：evaluation (JSON), score
   - 讲解内容：explanation (JSON)
   - 用时：time_spent

5. **分析文档模型 (analysis_documents)**
   - 文档信息：id, project_id, section_id
   - 内容：content (TEXT)
   - 版本：version
   - 时间戳：created_at, updated_at

6. **笔记模型 (notes)**
   - 笔记信息：id, session_id, question_id
   - 内容：content (TEXT), highlights (JSON)
   - 时间戳：created_at, updated_at

---

## 验收标准

- [ ] 所有模型类定义在 `infrastructure/models/` 目录
- [ ] 模型继承自 `infrastructure/models/base.py` 的 BaseModel
- [ ] 所有外键关系正确定义，包含级联删除策略
- [ ] JSON 字段使用 PostgreSQL 的 JSONB 类型
- [ ] 所有模型包含 created_at, updated_at 时间戳
- [ ] Alembic 迁移脚本生成成功：`alembic revision --autogenerate`
- [ ] 迁移执行成功：`alembic upgrade head`
- [ ] 迁移回滚成功：`alembic downgrade -1`
- [ ] 模型支持异步操作 (SQLAlchemy 2.0 async)

---

## 注意事项

1. **主键策略**
   - 使用 UUID 作为主键，格式：`proj_xxx`、`sess_xxx`、`q_xxx`
   - 或使用纯 UUID，在应用层添加前缀

2. **索引设计**
   - 为常用查询字段添加索引：project_id, session_id
   - 为状态字段添加索引：status
   - 为时间字段添加索引：created_at

3. **JSON 字段设计**
   - 使用 JSONB 类型支持索引和查询
   - 定义清晰的 JSON Schema 文档
   - 考虑未来的字段扩展

4. **软删除**
   - 考虑是否需要软删除（deleted_at 字段）

5. **迁移安全**
   - 迁移脚本应支持回滚
   - 大表添加索引使用 `CONCURRENTLY`
   - 生产环境迁移前先在测试环境验证

---

## 相关文档

- [架构设计文档 - 附录C 数据模型设计](../docs/code-learning-coach-architecture.md#c-数据模型设计-er-图)
- [Alembic 使用指南](../docs/alembic.md)
