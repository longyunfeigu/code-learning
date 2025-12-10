# TASK-018: 部署与运维

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-018 |
| **任务名称** | 部署与运维 |
| **版本** | V1.0 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 3-5 天 |
| **前置任务** | TASK-017 |

---

## 任务描述

完善 Docker 部署方案，配置生产环境所需的各项服务，实现可观测性（日志、监控、追踪），编写部署和运维文档。

### 主要工作内容

1. **Docker 镜像优化 (`Dockerfile`)**
   - 多阶段构建减小镜像体积
   - 使用非 root 用户运行
   - 优化依赖安装顺序
   - 配置健康检查

2. **Docker Compose 完善 (`docker-compose.yml`)**
   
   **服务清单：**
   - backend: FastAPI 应用
   - celery-worker: 异步任务处理
   - celery-beat: 定时任务调度
   - postgres: 主数据库
   - redis: 缓存和消息队列
   - qdrant: 向量数据库
   - minio: 对象存储
   - nginx: 反向代理 (可选)
   
   **网络配置：**
   - 内部网络隔离
   - 端口映射
   - 服务依赖顺序

3. **生产配置 (`docker-compose.prod.yml`)**
   - 资源限制 (CPU, Memory)
   - 重启策略
   - 日志驱动配置
   - 环境变量文件

4. **可观测性配置**
   
   **日志：**
   - structlog 结构化日志
   - 日志级别配置
   - 日志文件轮转
   - (可选) ELK Stack 集成
   
   **监控：**
   - Prometheus 指标暴露 `/metrics`
   - Grafana 仪表盘模板
   - 自定义业务指标
   
   **追踪：**
   - OpenTelemetry 集成
   - Jaeger 追踪后端
   - Agent 调用链追踪

5. **健康检查与告警**
   - `/health` 健康检查端点
   - 数据库连接检查
   - Redis 连接检查
   - LLM API 可用性检查
   - (可选) AlertManager 告警规则

6. **运维脚本 (`scripts/`)**
   - 数据库备份脚本
   - 数据库恢复脚本
   - 向量索引重建脚本
   - 日志清理脚本

---

## 验收标准

- [ ] `docker-compose up -d` 一键启动所有服务
- [ ] 服务启动后健康检查通过
- [ ] Prometheus 能采集到应用指标
- [ ] 日志输出为 JSON 格式
- [ ] API 请求有完整的追踪 ID
- [ ] 提供 Grafana 仪表盘模板
- [ ] 数据库备份脚本可用
- [ ] 部署文档完整清晰
- [ ] 生产环境配置与开发环境分离

---

## 注意事项

1. **Dockerfile 优化**
   ```dockerfile
   # 多阶段构建
   FROM python:3.11-slim as builder
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   FROM python:3.11-slim
   WORKDIR /app
   COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
   COPY . .
   
   # 非 root 用户
   RUN useradd -m appuser
   USER appuser
   
   # 健康检查
   HEALTHCHECK --interval=30s --timeout=5s \
     CMD curl -f http://localhost:8000/health || exit 1
   
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Docker Compose 服务依赖**
   ```yaml
   services:
     backend:
       depends_on:
         postgres:
           condition: service_healthy
         redis:
           condition: service_healthy
         qdrant:
           condition: service_started
   ```

3. **Prometheus 指标**
   ```python
   from prometheus_client import Counter, Histogram
   
   llm_requests = Counter(
       'llm_requests_total',
       'Total LLM API requests',
       ['model', 'status']
   )
   
   llm_latency = Histogram(
       'llm_request_duration_seconds',
       'LLM request latency',
       ['model']
   )
   ```

4. **健康检查端点**
   ```python
   @router.get("/health")
   async def health_check(
       db: AsyncSession = Depends(get_db),
       redis: Redis = Depends(get_redis),
   ):
       return {
           "status": "healthy",
           "database": await check_db(db),
           "redis": await check_redis(redis),
           "version": settings.version,
       }
   ```

5. **敏感信息处理**
   - 使用 `.env.prod` 文件
   - 生产密钥不提交到代码库
   - 使用 Docker secrets 管理敏感信息

---

## 相关文档

- [架构设计文档 - 3. 组件部署架构](../docs/code-learning-coach-architecture.md#3-组件部署架构)
- [架构设计文档 - 8.3 可观测性](../docs/code-learning-coach-architecture.md#83-可观测性)
- [架构设计文档 - 附录A 部署依赖关系](../docs/code-learning-coach-architecture.md#a-部署依赖关系)

