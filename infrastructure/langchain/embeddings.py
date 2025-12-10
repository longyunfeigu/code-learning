"""
Embedding 配置模块 - 通过 LangChain 统一封装

支持多种 Embedding 提供商：
- OpenAI (text-embedding-3-small/large)
- HuggingFace (BGE, etc.)

使用示例:
    >>> from infrastructure.langchain import get_embeddings
    >>> embeddings = get_embeddings()  # 使用默认配置
    >>> embeddings = get_embeddings(provider="openai", model="text-embedding-3-small")
    >>> vectors = await embeddings.aembed_documents(["Hello", "World"])
"""

from typing import Optional, Literal, List

from langchain_core.embeddings import Embeddings

from core.config import settings
from core.logging_config import get_logger
from .exceptions import EmbeddingProviderError, EmbeddingConfigError

logger = get_logger(__name__)

# Embedding 提供商类型
EmbeddingProvider = Literal["openai", "huggingface"]


def get_embeddings(
    provider: Optional[EmbeddingProvider] = None,
    model: Optional[str] = None,
) -> Embeddings:
    """
    获取 Embedding 实例 - 统一接口
    
    Args:
        provider: 提供商 (openai, huggingface)，默认从配置读取
        model: 模型名称，默认从配置读取
    
    Returns:
        Embeddings: LangChain Embeddings 实例
    
    Raises:
        EmbeddingProviderError: 不支持的 provider 或依赖未安装
        EmbeddingConfigError: 配置错误（如缺少 API Key）
    
    Example:
        >>> embeddings = get_embeddings()  # 使用默认配置
        >>> embeddings = get_embeddings(provider="openai", model="text-embedding-3-small")
        >>> embeddings = get_embeddings(provider="huggingface", model="BAAI/bge-small-zh")
    """
    provider = provider or settings.embedding.provider
    model = model or settings.embedding.model
    
    logger.debug(
        "creating_embeddings",
        provider=provider,
        model=model,
    )
    
    if provider == "openai":
        return _get_openai_embeddings(model)
    elif provider == "huggingface":
        return _get_huggingface_embeddings(model)
    else:
        raise EmbeddingProviderError(
            f"Unsupported embedding provider: {provider}. "
            f"Supported providers: openai, huggingface"
        )


def _get_openai_embeddings(model: str) -> Embeddings:
    """获取 OpenAI Embeddings"""
    try:
        from langchain_openai import OpenAIEmbeddings
    except ImportError:
        raise EmbeddingProviderError(
            "langchain-openai is required for OpenAI embeddings. "
            "Install with: pip install langchain-openai"
        )
    
    # 验证 API Key
    api_key = settings.openai.api_key
    if not api_key:
        raise EmbeddingConfigError(
            "OpenAI API key is not configured. "
            "Please set OPENAI__API_KEY in environment variables."
        )
    
    kwargs = {
        "model": model,
        "api_key": api_key.get_secret_value() if hasattr(api_key, 'get_secret_value') else api_key,
    }
    
    if settings.openai.base_url:
        kwargs["base_url"] = settings.openai.base_url
    
    logger.debug("openai_embeddings_created", model=model)
    return OpenAIEmbeddings(**kwargs)


def _get_huggingface_embeddings(model: str) -> Embeddings:
    """获取 HuggingFace Embeddings"""
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
    except ImportError:
        raise EmbeddingProviderError(
            "langchain-huggingface is required for HuggingFace embeddings. "
            "Install with: pip install langchain-huggingface"
        )
    
    logger.debug(
        "huggingface_embeddings_creating",
        model=model,
        device=settings.embedding.device,
    )
    
    return HuggingFaceEmbeddings(
        model_name=model,
        model_kwargs={"device": settings.embedding.device},
        encode_kwargs={"normalize_embeddings": True},
    )


# =============================================================================
# 缓存 Embeddings 实例
# =============================================================================

_embeddings_cache: dict[str, Embeddings] = {}


def get_cached_embeddings(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> Embeddings:
    """
    获取缓存的 Embeddings 实例
    
    用于频繁调用场景，避免重复创建实例和加载模型。
    特别对 HuggingFace 模型有效（模型加载耗时较长）。
    
    Args:
        provider: 提供商
        model: 模型名称
    
    Returns:
        Embeddings: 缓存的 Embeddings 实例
    """
    provider = provider or settings.embedding.provider
    model = model or settings.embedding.model
    
    cache_key = f"{provider}:{model}"
    
    if cache_key not in _embeddings_cache:
        _embeddings_cache[cache_key] = get_embeddings(provider=provider, model=model)
        logger.debug("embeddings_cached", cache_key=cache_key)
    
    return _embeddings_cache[cache_key]


def clear_embeddings_cache():
    """清除 Embeddings 缓存"""
    _embeddings_cache.clear()
    logger.debug("embeddings_cache_cleared")


# =============================================================================
# 批量嵌入工具函数
# =============================================================================

async def embed_documents_batch(
    texts: List[str],
    batch_size: Optional[int] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> List[List[float]]:
    """
    批量嵌入文档
    
    将大量文本分批处理，避免单次请求过大。
    
    Args:
        texts: 要嵌入的文本列表
        batch_size: 每批大小，默认从配置读取
        provider: Embedding 提供商
        model: 模型名称
    
    Returns:
        List[List[float]]: 嵌入向量列表
    
    Example:
        >>> texts = ["文档1", "文档2", "文档3", ...]
        >>> vectors = await embed_documents_batch(texts, batch_size=50)
    """
    batch_size = batch_size or settings.embedding.batch_size
    embeddings = get_cached_embeddings(provider=provider, model=model)
    
    all_vectors: List[List[float]] = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        logger.debug(
            "embedding_batch",
            batch_index=i // batch_size,
            batch_size=len(batch),
            total=len(texts),
        )
        
        # 使用异步方法
        batch_vectors = await embeddings.aembed_documents(batch)
        all_vectors.extend(batch_vectors)
    
    return all_vectors


def embed_documents_batch_sync(
    texts: List[str],
    batch_size: Optional[int] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> List[List[float]]:
    """
    批量嵌入文档（同步版本）
    
    Args:
        texts: 要嵌入的文本列表
        batch_size: 每批大小
        provider: Embedding 提供商
        model: 模型名称
    
    Returns:
        List[List[float]]: 嵌入向量列表
    """
    batch_size = batch_size or settings.embedding.batch_size
    embeddings = get_cached_embeddings(provider=provider, model=model)
    
    all_vectors: List[List[float]] = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        logger.debug(
            "embedding_batch_sync",
            batch_index=i // batch_size,
            batch_size=len(batch),
            total=len(texts),
        )
        
        batch_vectors = embeddings.embed_documents(batch)
        all_vectors.extend(batch_vectors)
    
    return all_vectors
