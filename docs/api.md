# API 层设计与使用指南（api/）

本层是系统的 HTTP 表现层（Controller）。职责是：
- 将 HTTP 输入/输出与应用用例解耦（只做 I/O 绑定与依赖注入）。
- 进行边界校验（Pydantic DTO）与安全控制（认证/授权）。
- 调用 Application Service 执行业务，不直接访问数据库/外部 SDK。

目录：
- 依赖与安全：`api/dependencies.py`
- 中间件：`api/middleware/request_id.py`、`api/middleware/logging.py`
- 路由：`api/routes/storage.py`、`api/routes/files.py`
- 工具：`api/utils/headers.py`

---

## 中间件

1) Request ID（追踪） — `api/middleware/request_id.py`
- 在每个请求生成或透传 `X-Request-ID`，写入 `request.state` 与 `contextvars`。
- 绑定到 structlog 日志上下文：`request_id`、`client_ip`、`method`、`path`。
- 响应头会返回同一个 `X-Request-ID` 便于调用方链路追踪。

2) 请求/响应日志 — `api/middleware/logging.py`
- 记录方法、路径、查询参数、路径参数、状态码、耗时等。
- 请求体记录可控：
  - 默认由 `settings.LOG_REQUEST_BODY_ENABLE_BY_DEFAULT` + `DEBUG` 决定。
  - 可用请求头覆盖：`X-Log-Body: true|false`。
  - 截断前 N 字节（默认 2048）并对敏感字段脱敏：`password`/`secret`/`api_key` 等。
  - `multipart/form-data` 默认不读取以避免大文件开销（可配置仅记录标记）。

---

## 依赖与安全（dependencies.py）
- 应用服务依赖：
  - `get_user_service()` — 注入 `UserApplicationService(uow_factory=SQLAlchemyUnitOfWork)`。
  - 文件资产相关通过端口：`get_storage_port()` 注入 `StoragePort` 适配器，`get_file_asset_service()` 组合 UoW + StoragePort。

要点：API 层不触达 ORM 或外部 SDK；一切通过 Application Service 与 Port 完成。

---

## 路由设计

- 存储（/api/v1/storage） — `api/routes/storage.py`
  - 直传预签名：`POST /presign-upload` → 返回预签名与 pending 记录摘要（不包含临时签名入库）。
  - 直传完成：`POST /complete` → 根据 `id` 或 `key` 回填元数据并激活。
  - 中转上传：`POST /upload` → API 接收文件后写入对象存储并 upsert 活跃资产。

- 文件管理（/api/v1/files） — `api/routes/files.py`
  - 列表：分页、条件过滤；可选 `signed=true` 在响应时动态覆盖 URL 为临时签名（不入库）。
  - 详情：支持 `signed` 与 `filename` 参数以控制下载/预览文件名与有效期。
  - 生成预览/下载链接：`/{asset_id}/preview-url`、`/{asset_id}/download-url`。
  - 删除：软删或物理删除（超管/本人）。


---

## 统一响应与异常
- 成功：`core/response.py:success_response()`。
- 失败：统一由 `core/exceptions.register_exception_handlers()` 生成 `Response[error]`，包含 `request_id` 与 UTC-Z 时间戳，业务码见 `shared/codes.py`。

---

## 示例（cURL）

(暂无示例)


---

## 编码准则（API 层）
- Controller 保持“瘦”：不做业务、不做数据访问。
- 所有日志通过 `core.logging_config.get_logger(__name__)`，不要使用 `print`。
- DTO/Response 作为对外契约；不要将 ORM 模型直接泄露到 API。
- 对外字段/行为如需变更，先改 DTO 与 Service，再改路由，避免跨层耦合。

---

## 删除策略（文件资源）

- 默认仅支持“软删除”：`DELETE /api/v1/files/{asset_id}` 将资源标记为 `deleted`（不会立即移除对象存储上的文件）。
- 物理删除（远端对象 + DB 记录）仅在服务内部提供：`FileAssetApplicationService.purge_asset_by_id(key)` 等，不对外暴露开关以避免误删。
- 推荐操作顺序：
  - 业务删除 → 软删（可恢复/审计）。
  - 后台保留清理任务按策略批量“物理删除”真正无引用的对象（如超期、回收站清空）。

---

## 安全建议

- 配置：
  - 强制设置 `SECRET_KEY`；生产环境使用高强度、唯一密钥。
  - 合理配置 CORS；默认开发便捷设置不要用于生产。
    - 日志：
  - 使用结构化日志；请求体记录遵守脱敏与体积限制；禁止输出密钥/令牌。
- 访问控制：
  - 所有文件写入/删除均要求登录；跨租户/可见范围由应用层校验（如 `owner_id`）。

---

