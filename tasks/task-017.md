# TASK-017: 测试与质量保障

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-017 |
| **任务名称** | 测试与质量保障 |
| **版本** | V1.0 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 5-7 天 |
| **前置任务** | TASK-001 ~ TASK-016 |

---

## 任务描述

建立完整的测试体系，包括单元测试、集成测试、端到端测试，确保代码质量和系统稳定性。配置测试覆盖率报告和 CI 自动化测试。

### 主要工作内容

1. **单元测试 (`tests/unit/`)**
   
   **领域层测试：**
   - 实体业务方法测试
   - 值对象不可变性测试
   - 领域服务逻辑测试
   - 领域事件触发测试
   
   **应用层测试：**
   - 服务方法测试（Mock 仓储）
   - DTO 转换测试
   - 业务流程测试
   
   **基础设施层测试：**
   - LangChain 封装测试（Mock LLM）
   - 仓储实现测试（内存数据库）
   - 代码分析服务测试

2. **集成测试 (`tests/integration/`)**
   
   **数据库集成测试：**
   - 仓储 CRUD 测试
   - 事务回滚测试
   - 迁移脚本测试
   
   **API 集成测试：**
   - 完整 API 流程测试
   - 错误处理测试
   
   **Agent 集成测试：**
   - 子 Agent 调用测试
   - 主 Agent 编排测试
   - WebSocket 通信测试

3. **端到端测试 (`tests/e2e/`)**
   - 完整学习流程测试
   - 项目分析流程测试
   - 学习会话流程测试

4. **测试配置 (`tests/conftest.py`)**
   - pytest 插件配置
   - 测试 fixtures
   - Mock 工厂
   - 测试数据生成

5. **测试覆盖率**
   - 配置 pytest-cov
   - 覆盖率目标：80%+
   - 覆盖率报告生成

6. **代码质量检查**
   - Ruff (Linter)
   - Black (Formatter)
   - mypy (类型检查)
   - pre-commit hooks

---

## 验收标准

- [ ] 单元测试覆盖率 >= 80%
- [ ] 所有 API 接口有对应的集成测试
- [ ] 核心业务流程有端到端测试
- [ ] 测试运行时间 < 5 分钟
- [ ] CI 管道自动运行测试
- [ ] 测试失败阻止合并
- [ ] Ruff 检查无错误
- [ ] mypy 类型检查无错误
- [ ] 覆盖率报告自动生成

---

## 注意事项

1. **单元测试示例**
   ```python
   # tests/unit/domain/test_project.py
   import pytest
   from domain.entities import Project, ProjectStatus
   from domain.events import ProjectAnalysisStarted
   
   def test_project_start_analysis():
       # Arrange
       project = Project.create("https://github.com/test/repo")
       
       # Act
       project.start_analysis()
       
       # Assert
       assert project.status == ProjectStatus.PROCESSING
       assert len(project.domain_events) == 1
       assert isinstance(project.domain_events[0], ProjectAnalysisStarted)
   
   def test_project_start_analysis_invalid_state():
       project = Project.create("https://github.com/test/repo")
       project.status = ProjectStatus.READY
       
       with pytest.raises(InvalidStateError):
           project.start_analysis()
   ```

2. **API 集成测试示例**
   ```python
   # tests/integration/api/test_projects.py
   import pytest
   from httpx import AsyncClient
   
   @pytest.mark.asyncio
   async def test_create_project(client: AsyncClient):
       response = await client.post(
           "/api/v1/projects",
           json={"repo_url": "https://github.com/test/repo"},
       )
       assert response.status_code == 200
       data = response.json()
       assert data["code"] == 0
       assert "project_id" in data["data"]
   ```

3. **Mock LLM 测试**
   ```python
   # tests/conftest.py
   from unittest.mock import AsyncMock
   
   @pytest.fixture
   def mock_llm():
       llm = AsyncMock()
       llm.agenerate.return_value = MockResponse(content="测试回复")
       return llm
   ```

4. **测试数据库**
   - 使用 SQLite 内存数据库
   - 或使用 Docker 启动临时 PostgreSQL
   - 每个测试后回滚事务

5. **CI 配置**
   ```yaml
   # .github/workflows/test.yml
   - name: Run tests
     run: |
       pytest tests/ --cov=. --cov-report=xml
   - name: Upload coverage
     uses: codecov/codecov-action@v3
   ```

---

## 相关文档

- [pytest 文档](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [httpx 测试](https://www.python-httpx.org/async/)
