# TASK-013: WebSocket 实时对话

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-013 |
| **任务名称** | WebSocket 实时对话 |
| **版本** | V0.5 |
| **状态** | 🔵 规划中 |
| **优先级** | P1 - 高 |
| **预计工时** | 2-3 天 |
| **前置任务** | TASK-011, TASK-012 |

---

## 任务描述

实现 WebSocket 实时对话接口，支持与 Learning Coach Agent 的交互式学习会话。实现流式响应、状态推送、连接管理等功能。

### 主要工作内容

1. **WebSocket 路由 (`api/routes/agents.py`)**
   
   | 路径 | 描述 |
   |------|------|
   | `/ws/agents/{session_id}` | Agent 实时对话 |
   | `/ws/projects/{project_id}/status` | 项目分析状态推送 |

2. **消息协议定义**
   
   **客户端 → 服务端：**
   ```json
   {
     "type": "message",
     "content": "对话消息内容",
     "metadata": {
       "question_id": "q_001"
     }
   }
   ```
   
   **服务端 → 客户端（流式响应）：**
   ```json
   {
     "type": "stream_start",
     "message_id": "msg_xxx"
   }
   {
     "type": "stream_chunk",
     "message_id": "msg_xxx",
     "content": "部分内容..."
   }
   {
     "type": "stream_end",
     "message_id": "msg_xxx",
     "total_content": "完整内容"
   }
   ```
   
   **服务端 → 客户端（状态更新）：**
   ```json
   {
     "type": "progress_update",
     "data": {
       "stage": "整体架构分析",
       "completed": 3,
       "total": 10
     }
   }
   ```

3. **连接管理 (`infrastructure/websocket/`)**
   - 连接池管理
   - 心跳检测
   - 断线重连支持
   - 会话状态关联

4. **Agent 集成**
   - 调用 DeepAgents 主 Agent
   - 流式输出转换为 WebSocket 消息
   - 错误处理和重试

---

## 验收标准

- [ ] WebSocket 连接建立成功率 > 99%
- [ ] 支持流式响应，首字节时间 < 2 秒
- [ ] 心跳间隔 30 秒，超时 60 秒断开
- [ ] 支持断线后自动重连
- [ ] 消息顺序保证正确
- [ ] 支持多客户端同时连接同一会话
- [ ] 连接数限制：每会话最多 5 个连接
- [ ] 错误消息格式规范
- [ ] 提供连接状态查询接口

---

## 注意事项

1. **FastAPI WebSocket 实现**
   ```python
   from fastapi import WebSocket, WebSocketDisconnect
   
   @router.websocket("/ws/agents/{session_id}")
   async def agent_chat(
       websocket: WebSocket,
       session_id: str,
   ):
       await websocket.accept()
       try:
           while True:
               data = await websocket.receive_json()
               # 处理消息
               async for chunk in agent.astream(data["content"]):
                   await websocket.send_json({
                       "type": "stream_chunk",
                       "content": chunk
                   })
       except WebSocketDisconnect:
           # 清理资源
           pass
   ```

2. **流式输出处理**
   ```python
   async for event in agent.astream_events(message):
       if event["event"] == "on_chat_model_stream":
           chunk = event["data"]["chunk"]
           await websocket.send_json({
               "type": "stream_chunk",
               "content": chunk.content
           })
   ```

3. **连接池管理**
   - 使用 Redis 存储连接映射
   - 支持集群环境下的消息路由
   - 定期清理过期连接

4. **错误处理**
   - Agent 错误不应断开连接
   - 发送错误消息给客户端
   - 记录详细错误日志

5. **性能优化**
   - 使用异步 IO
   - 消息批量发送
   - 压缩大消息

---

## 相关文档

- [架构设计文档 - 附录D API 接口清单](../docs/code-learning-coach-architecture.md#d-api-接口清单)
- [架构设计文档 - 4.3 问题驱动学习流程](../docs/code-learning-coach-architecture.md#43-问题驱动学习流程-socratic-tutoring)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
