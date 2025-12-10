"""
能力模块定义

定义可识别和深挖学习的能力模块。
"""

from enum import Enum
from typing import Dict, List


class CapabilityModule(str, Enum):
    """能力模块枚举"""
    
    # Agent 相关
    AGENT_HARNESS = "agent_harness"
    """Agent 运行时/编排框架"""
    
    TOOL_SYSTEM = "tool_system"
    """工具系统 - 工具注册、调用、管理"""
    
    STATE_MANAGEMENT = "state_management"
    """状态管理 - Agent 状态持久化和流转"""
    
    # 系统能力
    PLUGIN_SYSTEM = "plugin_system"
    """插件/扩展系统"""
    
    MIDDLEWARE_PIPELINE = "middleware_pipeline"
    """中间件管道"""
    
    EVENT_SYSTEM = "event_system"
    """事件系统 - 发布/订阅"""
    
    # 数据处理
    CACHE_LAYER = "cache_layer"
    """缓存层"""
    
    DATA_ACCESS = "data_access"
    """数据访问层 - Repository、ORM"""
    
    # 安全和运维
    AUTH_SYSTEM = "auth_system"
    """认证/授权系统"""
    
    ERROR_HANDLING = "error_handling"
    """错误处理机制"""
    
    OBSERVABILITY = "observability"
    """可观测性 - 日志、指标、追踪"""
    
    # 通信
    API_LAYER = "api_layer"
    """API 层 - 路由、序列化"""
    
    MESSAGING = "messaging"
    """消息队列集成"""
    
    REALTIME = "realtime"
    """实时通信 - WebSocket"""


# 能力模块识别特征
CAPABILITY_FEATURES: Dict[CapabilityModule, Dict[str, List[str]]] = {
    CapabilityModule.AGENT_HARNESS: {
        "directories": ["agents", "orchestrator", "runtime", "harness"],
        "files": ["agent.py", "runtime.py", "orchestrator.py"],
        "patterns": ["StateGraph", "AgentExecutor", "create_agent"],
    },
    CapabilityModule.TOOL_SYSTEM: {
        "directories": ["tools", "functions"],
        "files": ["tools.py", "functions.py"],
        "patterns": ["@tool", "Tool", "FunctionTool", "register_tool"],
    },
    CapabilityModule.STATE_MANAGEMENT: {
        "directories": ["state", "store"],
        "files": ["state.py", "store.py"],
        "patterns": ["TypedDict", "StateSnapshot", "Checkpoint"],
    },
    CapabilityModule.PLUGIN_SYSTEM: {
        "directories": ["plugins", "extensions", "addons"],
        "files": ["plugin.py", "extension.py"],
        "patterns": ["PluginBase", "register_plugin", "load_plugins"],
    },
    CapabilityModule.MIDDLEWARE_PIPELINE: {
        "directories": ["middleware", "middlewares"],
        "files": ["middleware.py"],
        "patterns": ["Middleware", "add_middleware", "use"],
    },
    CapabilityModule.EVENT_SYSTEM: {
        "directories": ["events", "pubsub"],
        "files": ["events.py", "publisher.py", "subscriber.py"],
        "patterns": ["Event", "emit", "subscribe", "publish"],
    },
    CapabilityModule.CACHE_LAYER: {
        "directories": ["cache"],
        "files": ["cache.py", "redis_cache.py"],
        "patterns": ["@cache", "Cache", "RedisCache", "get_cache"],
    },
    CapabilityModule.DATA_ACCESS: {
        "directories": ["repositories", "models", "dao"],
        "files": ["repository.py", "models.py"],
        "patterns": ["Repository", "BaseModel", "Session", "Query"],
    },
    CapabilityModule.AUTH_SYSTEM: {
        "directories": ["auth", "security"],
        "files": ["auth.py", "security.py", "jwt.py"],
        "patterns": ["authenticate", "authorize", "JWT", "OAuth"],
    },
    CapabilityModule.ERROR_HANDLING: {
        "directories": ["exceptions"],
        "files": ["exceptions.py", "errors.py"],
        "patterns": ["Exception", "ErrorHandler", "try", "except"],
    },
    CapabilityModule.OBSERVABILITY: {
        "directories": ["logging", "metrics", "tracing"],
        "files": ["logging.py", "metrics.py", "tracing.py"],
        "patterns": ["logger", "metric", "span", "trace"],
    },
    CapabilityModule.API_LAYER: {
        "directories": ["api", "routes", "controllers"],
        "files": ["routes.py", "api.py"],
        "patterns": ["@router", "@app.get", "APIRouter"],
    },
    CapabilityModule.MESSAGING: {
        "directories": ["messaging", "queue", "kafka"],
        "files": ["producer.py", "consumer.py"],
        "patterns": ["Producer", "Consumer", "publish", "subscribe"],
    },
    CapabilityModule.REALTIME: {
        "directories": ["websocket", "realtime"],
        "files": ["websocket.py", "realtime.py"],
        "patterns": ["WebSocket", "socket", "broadcast"],
    },
}


# 能力模块描述
CAPABILITY_DESCRIPTIONS: Dict[CapabilityModule, str] = {
    CapabilityModule.AGENT_HARNESS: "Agent 运行时框架，负责 Agent 生命周期管理和编排",
    CapabilityModule.TOOL_SYSTEM: "工具系统，管理 Agent 可调用的工具",
    CapabilityModule.STATE_MANAGEMENT: "状态管理，处理 Agent 状态的存储和流转",
    CapabilityModule.PLUGIN_SYSTEM: "插件系统，支持功能扩展",
    CapabilityModule.MIDDLEWARE_PIPELINE: "中间件管道，处理请求/响应流水线",
    CapabilityModule.EVENT_SYSTEM: "事件系统，实现解耦的组件通信",
    CapabilityModule.CACHE_LAYER: "缓存层，提升数据访问性能",
    CapabilityModule.DATA_ACCESS: "数据访问层，封装数据库操作",
    CapabilityModule.AUTH_SYSTEM: "认证授权系统，保护资源安全",
    CapabilityModule.ERROR_HANDLING: "错误处理机制，优雅处理异常",
    CapabilityModule.OBSERVABILITY: "可观测性，日志、指标、追踪",
    CapabilityModule.API_LAYER: "API 层，处理外部请求",
    CapabilityModule.MESSAGING: "消息队列，异步通信",
    CapabilityModule.REALTIME: "实时通信，WebSocket 支持",
}

