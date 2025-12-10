"""
配置文件 - 项目配置管理

包含所有配置类定义，支持从环境变量读取配置。
使用嵌套配置时，环境变量使用双下划线分隔：SECTION__KEY
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field, SecretStr, field_validator
from typing import Optional, Literal
from pydantic import model_validator


# =============================================================================
# 基础设施配置
# =============================================================================

class GrpcTlsSettings(BaseModel):
    enabled: bool = False
    cert: Optional[str] = None
    key: Optional[str] = None
    ca: Optional[str] = None


class GrpcSettings(BaseModel):
    enabled: bool = False
    host: str = "0.0.0.0"
    port: int = 50051
    max_concurrent_streams: int = 100
    tls: GrpcTlsSettings = Field(default_factory=GrpcTlsSettings)


class KafkaSettings(BaseModel):
    # Provider/driver
    provider: str = Field(default="kafka")
    driver: str = Field(default="confluent")  # confluent or aiokafka

    # Core Kafka
    bootstrap_servers: str = Field(default="localhost:9092")
    client_id: str = Field(default="app-messaging")
    transactional_id: Optional[str] = None

    # TLS
    tls_enable: bool = False
    tls_ca_location: Optional[str] = None
    tls_certificate: Optional[str] = None
    tls_key: Optional[str] = None
    tls_verify: bool = True

    # SASL
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None

    # Producer tuning
    producer_acks: str = "all"
    producer_enable_idempotence: bool = True
    producer_compression_type: str = "zstd"
    producer_linger_ms: int = 5
    producer_batch_size: int = 64 * 1024
    producer_max_in_flight: int = 5
    producer_message_timeout_ms: int = 120_000
    producer_send_wait_s: float = 5.0
    producer_delivery_wait_s: float = 30.0

    # Consumer tuning
    consumer_enable_auto_commit: bool = False
    consumer_auto_offset_reset: str = "latest"
    consumer_max_poll_interval_ms: int = 300000
    consumer_session_timeout_ms: int = 45000
    consumer_fetch_min_bytes: int = 1
    consumer_fetch_max_bytes: int = 50 * 1024 * 1024
    consumer_commit_every_n: int = 100
    consumer_commit_interval_ms: int = 2000
    consumer_max_concurrency: int = 1
    consumer_inflight_max: int = 1000

    # Retry policy
    retry_layers: Optional[str] = "retry.5s:5000,retry.1m:60000,retry.10m:600000"
    retry_dlq_suffix: str = "dlq"


class RedisSettings(BaseModel):
    url: Optional[str] = None
    max_connections: int = 10
    default_ttl: int = 300
    namespace: str = "fastapi-forge"


class DatabaseSettings(BaseModel):
    url: str = "postgresql+asyncpg://user:password@localhost/userdb"


class StorageSettings(BaseModel):
    type: str = "local"  # local, s3, oss
    bucket: Optional[str] = None
    region: Optional[str] = None
    endpoint: Optional[str] = None
    public_base_url: Optional[str] = None
    # S3 specific
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    s3_sse: Optional[str] = None
    s3_acl: str = "private"
    # OSS specific
    oss_access_key_id: Optional[str] = None
    oss_access_key_secret: Optional[str] = None
    # Local storage specific
    local_base_path: str = "/tmp/storage"
    # Advanced settings
    max_retry_attempts: int = 3
    timeout: int = 30
    enable_ssl: bool = True
    presign_max_size: int = 100 * 1024 * 1024  # 100MB
    presign_content_types: Optional[list[str]] = None
    validation_enabled: bool = False
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_types: Optional[list[str]] = None


# =============================================================================
# LLM 和 AI 相关配置
# =============================================================================

class OpenAISettings(BaseModel):
    """OpenAI 配置"""
    api_key: Optional[SecretStr] = Field(
        default=None,
        description="OpenAI API Key"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="OpenAI API Base URL (可选，用于代理或兼容 API)"
    )
    organization: Optional[str] = Field(
        default=None,
        description="OpenAI Organization ID"
    )


class AnthropicSettings(BaseModel):
    """Anthropic (Claude) 配置"""
    api_key: Optional[SecretStr] = Field(
        default=None,
        description="Anthropic API Key"
    )


class OllamaSettings(BaseModel):
    """Ollama 本地模型配置"""
    base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama 服务地址"
    )


class LLMSettings(BaseModel):
    """LLM 统一配置"""
    provider: Literal["openai", "anthropic", "ollama"] = Field(
        default="openai",
        description="LLM 提供商"
    )
    model: str = Field(
        default="gpt-4-turbo",
        description="默认模型名称"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="生成温度"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        description="最大生成 token 数"
    )
    timeout: int = Field(
        default=60,
        description="请求超时时间（秒）"
    )
    max_retries: int = Field(
        default=3,
        description="最大重试次数"
    )


class EmbeddingSettings(BaseModel):
    """Embedding 配置"""
    provider: Literal["openai", "huggingface"] = Field(
        default="openai",
        description="Embedding 提供商"
    )
    model: str = Field(
        default="text-embedding-3-small",
        description="Embedding 模型名称"
    )
    device: str = Field(
        default="cpu",
        description="HuggingFace 模型运行设备 (cpu/cuda)"
    )
    batch_size: int = Field(
        default=100,
        description="批量处理大小"
    )


# =============================================================================
# 向量数据库配置
# =============================================================================

class ChromaSettings(BaseModel):
    """Chroma 向量数据库配置"""
    persist_directory: str = Field(
        default="./data/chroma",
        description="持久化目录"
    )
    host: Optional[str] = Field(
        default=None,
        description="Chroma 服务器地址 (客户端-服务器模式)"
    )
    port: Optional[int] = Field(
        default=None,
        description="Chroma 服务器端口"
    )


class VectorStoreSettings(BaseModel):
    """向量数据库统一配置"""
    provider: Literal["chroma"] = Field(
        default="chroma",
        description="向量数据库提供商（仅支持 chroma）"
    )
    default_collection: str = Field(
        default="default",
        description="默认集合名称"
    )


# =============================================================================
# 对象存储配置 (MinIO/S3)
# =============================================================================

class MinioSettings(BaseModel):
    """MinIO 对象存储配置"""
    endpoint: str = Field(
        default="localhost:9000",
        description="MinIO 端点"
    )
    access_key: Optional[SecretStr] = Field(
        default=None,
        description="Access Key"
    )
    secret_key: Optional[SecretStr] = Field(
        default=None,
        description="Secret Key"
    )
    bucket: str = Field(
        default="code-learning",
        description="默认 Bucket"
    )
    secure: bool = Field(
        default=False,
        description="是否使用 HTTPS"
    )


# =============================================================================
# Git 和代码分析配置
# =============================================================================

class GitSettings(BaseModel):
    """Git 相关配置"""
    workspace_dir: str = Field(
        default="./data/repos",
        description="仓库克隆工作目录"
    )
    default_clone_depth: int = Field(
        default=1,
        description="默认克隆深度 (shallow clone)"
    )
    clone_timeout: int = Field(
        default=300,
        description="克隆超时时间（秒）"
    )


class CodeAnalysisSettings(BaseModel):
    """代码分析配置"""
    max_file_size: int = Field(
        default=1024 * 1024,  # 1MB
        description="最大文件大小（字节）"
    )
    chunk_size: int = Field(
        default=1000,
        description="代码片段大小（字符）"
    )
    chunk_overlap: int = Field(
        default=200,
        description="片段重叠大小"
    )
    supported_languages: list[str] = Field(
        default=["python", "typescript", "javascript", "java", "go", "rust"],
        description="支持的编程语言"
    )


# =============================================================================
# 主配置类
# =============================================================================

class Settings(BaseSettings):
    """项目配置"""
    
    # 基础配置
    PROJECT_NAME: str = Field(
        default="Code Learning Coach",
        env=["PROJECT_NAME", "APP_NAME"]
    )
    VERSION: str = Field(
        default="1.0.0",
        env=["VERSION", "APP_VERSION"]
    )
    DEBUG: bool = Field(
        default=True,
        env="DEBUG"
    )
    ENVIRONMENT: str = Field(
        default="development",
        env="ENVIRONMENT"
    )
    
    # 安全配置
    SECRET_KEY: Optional[str] = Field(
        default=None,
        env="SECRET_KEY",
        description="应用密钥，生产环境必须设置"
    )
    
    # CORS配置
    CORS_ORIGINS: list = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )
    
    # 基础设施配置
    kafka: KafkaSettings = Field(default_factory=KafkaSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    grpc: GrpcSettings = Field(default_factory=GrpcSettings)
    
    # LLM 配置
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    
    # Embedding 配置
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    
    # 向量数据库配置（仅 Chroma）
    chroma: ChromaSettings = Field(default_factory=ChromaSettings)
    vectorstore: VectorStoreSettings = Field(default_factory=VectorStoreSettings)
    
    # 对象存储配置
    minio: MinioSettings = Field(default_factory=MinioSettings)
    
    # Git 和代码分析配置
    git: GitSettings = Field(default_factory=GitSettings)
    code_analysis: CodeAnalysisSettings = Field(default_factory=CodeAnalysisSettings)
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    MAX_PAGE_SIZE: int = Field(default=100, env="MAX_PAGE_SIZE")

    # 日志/请求体记录配置
    LOG_REQUEST_BODY_ENABLE_BY_DEFAULT: bool = Field(
        default=True,
        env="LOG_REQUEST_BODY_ENABLE_BY_DEFAULT"
    )
    LOG_REQUEST_BODY_MAX_BYTES: int = Field(
        default=2048,
        env="LOG_REQUEST_BODY_MAX_BYTES"
    )
    LOG_REQUEST_BODY_ALLOW_MULTIPART: bool = Field(
        default=False,
        env="LOG_REQUEST_BODY_ALLOW_MULTIPART"
    )

    # 文件日志配置
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_MAX_BYTES: int = Field(default=100 * 1024 * 1024, env="LOG_MAX_BYTES")
    LOG_BACKUP_COUNT: int = Field(default=5, env="LOG_BACKUP_COUNT")

    # Redis 锁配置
    REDIS_LOCK_AUTO_RENEW_DEFAULT: bool = Field(
        default=False,
        env="REDIS_LOCK_AUTO_RENEW_DEFAULT"
    )
    REDIS_LOCK_AUTO_RENEW_INTERVAL_RATIO: float = Field(
        default=0.6,
        env="REDIS_LOCK_AUTO_RENEW_INTERVAL_RATIO"
    )
    REDIS_LOCK_AUTO_RENEW_JITTER_RATIO: float = Field(
        default=0.1,
        env="REDIS_LOCK_AUTO_RENEW_JITTER_RATIO"
    )

    # pydantic-settings v2 配置
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow",
        env_nested_delimiter="__",
    )

    @model_validator(mode="after")
    def _validate_secret_key(self):
        """验证 SECRET_KEY 必须配置"""
        if not self.SECRET_KEY:
            raise ValueError(
                "SECRET_KEY 未配置。请在环境变量或 .env 中设置 SECRET_KEY"
            )
        return self

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v):
        """解析 CORS_ORIGINS，支持 JSON 字符串或逗号分隔"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("[") and s.endswith("]"):
                import json
                try:
                    arr = json.loads(s)
                    if isinstance(arr, list):
                        return arr
                except Exception:
                    pass
            if "," in s:
                return [item.strip() for item in s.split(",") if item.strip()]
            return [s]
        return v


# 全局配置实例
settings = Settings()
