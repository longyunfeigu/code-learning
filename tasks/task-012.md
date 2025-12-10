# TASK-012: REST API 路由实现

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-012 |
| **任务名称** | REST API 路由实现 |
| **版本** | V0.5 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 3-4 天 |
| **前置任务** | TASK-007, TASK-011 |

---

## 任务描述

实现完整的 REST API 路由层，包括项目管理、学习会话、问题系统、分析文档、笔记管理等接口。遵循项目的 API 规范和响应格式。

### 主要工作内容

1. **项目管理接口 (`api/routes/projects.py`)**
   
   | 方法 | 路径 | 描述 |
   |------|------|------|
   | POST | `/api/v1/projects` | 创建项目（提交仓库 URL） |
   | GET | `/api/v1/projects` | 获取项目列表 |
   | GET | `/api/v1/projects/{id}` | 获取项目详情 |
   | GET | `/api/v1/projects/{id}/status` | 获取分析状态 |
   | DELETE | `/api/v1/projects/{id}` | 删除项目 |
   | GET | `/api/v1/projects/{id}/profile` | 获取项目画像 |
   | GET | `/api/v1/projects/{id}/repo-map` | 获取代码地图 |
   | GET | `/api/v1/projects/{id}/capabilities` | 获取能力模块列表 |

2. **学习会话接口 (`api/routes/sessions.py`)**
   
   | 方法 | 路径 | 描述 |
   |------|------|------|
   | POST | `/api/v1/sessions` | 创建学习会话 |
   | GET | `/api/v1/sessions` | 获取会话列表 |
   | GET | `/api/v1/sessions/{id}` | 获取会话详情 |
   | PATCH | `/api/v1/sessions/{id}` | 更新会话状态（暂停/恢复） |
   | DELETE | `/api/v1/sessions/{id}` | 删除会话 |
   | GET | `/api/v1/sessions/{id}/progress` | 获取学习进度 |

3. **问题系统接口 (`api/routes/questions.py`)**
   
   | 方法 | 路径 | 描述 |
   |------|------|------|
   | GET | `/api/v1/sessions/{id}/questions` | 获取问题列表 |
   | GET | `/api/v1/sessions/{id}/questions/current` | 获取当前问题 |
   | GET | `/api/v1/questions/{id}` | 获取问题详情 |
   | POST | `/api/v1/sessions/{id}/answers` | 提交回答 |
   | GET | `/api/v1/sessions/{id}/answers` | 获取回答历史 |
   | POST | `/api/v1/questions/{id}/skip` | 跳过问题 |

4. **分析文档接口 (`api/routes/analysis.py`)**
   
   | 方法 | 路径 | 描述 |
   |------|------|------|
   | GET | `/api/v1/analysis/{project_id}` | 获取完整分析文档 |
   | GET | `/api/v1/analysis/{project_id}/sections` | 获取章节列表 |
   | GET | `/api/v1/analysis/{project_id}/sections/{section_id}` | 获取单章节 |
   | POST | `/api/v1/analysis/{project_id}/regenerate` | 重新生成分析 |
   | GET | `/api/v1/analysis/{project_id}/export` | 导出文档 |

5. **笔记管理接口 (`api/routes/notes.py`)**
   
   | 方法 | 路径 | 描述 |
   |------|------|------|
   | GET | `/api/v1/sessions/{id}/notes` | 获取会话笔记 |
   | POST | `/api/v1/sessions/{id}/notes` | 创建笔记 |
   | PUT | `/api/v1/notes/{id}` | 更新笔记 |
   | DELETE | `/api/v1/notes/{id}` | 删除笔记 |

6. **请求/响应 Schema (`api/schemas/`)**
   - 使用 Pydantic v2 定义
   - 请求验证
   - 响应序列化
   - OpenAPI 文档生成

---

## 验收标准

- [ ] 所有接口遵循 RESTful 规范
- [ ] 响应格式统一使用 `core/response.py` 定义的格式
- [ ] 所有接口包含完整的 Pydantic Schema
- [ ] OpenAPI 文档自动生成且可访问 `/docs`
- [ ] 接口支持分页查询 (page, page_size)
- [ ] 接口支持字段过滤 (fields 参数)
- [ ] 错误响应包含明确的错误码和消息
- [ ] 接口响应时间 < 500ms (不含 LLM 调用)
- [ ] 单元测试覆盖所有接口

---

## 注意事项

1. **响应格式规范**
   ```json
   {
     "code": 0,
     "message": "success",
     "data": { ... },
     "meta": {
       "page": 1,
       "page_size": 20,
       "total": 100
     }
   }
   ```

2. **错误响应规范**
   ```json
   {
     "code": 40001,
     "message": "项目不存在",
     "data": null,
     "errors": [
       {"field": "project_id", "message": "无效的项目 ID"}
     ]
   }
   ```

3. **依赖注入**
   ```python
   @router.post("/projects")
   async def create_project(
       request: CreateProjectRequest,
       uow: UnitOfWork = Depends(get_uow),
   ):
       ...
   ```

4. **异步处理**
   - 项目分析等耗时操作返回任务 ID
   - 客户端轮询状态或使用 WebSocket

---

## 相关文档

- [架构设计文档 - 附录D API 接口清单](../docs/code-learning-coach-architecture.md#d-api-接口清单)
- [架构设计文档 - 4.1 项目初始化流程](../docs/code-learning-coach-architecture.md#41-项目初始化流程)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
