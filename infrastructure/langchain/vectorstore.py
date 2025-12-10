"""向量数据库配置模块 - 通过 LangChain 统一封装

支持多种向量数据库：
- Chroma (默认，开发/测试/小规模生产)
- Qdrant (可选，生产级)
- PGVector (PostgreSQL 扩展)

使用示例:
    >>> from infrastructure.langchain import get_vectorstore
    >>> vs = get_vectorstore("code_chunks")  # 默认使用 Chroma
    >>> vs = get_vectorstore("docs", provider="chroma")
    >>> await vs.aadd_documents(documents)
"""

from typing import Optional, Literal, List, Any

from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document

from core.config import settings
from core.logging_config import get_logger
from .embeddings import get_embeddings
from .exceptions import VectorStoreProviderError

logger = get_logger(__name__)

# VectorStore 提供商类型（仅保留 chroma）
VectorStoreProvider = Literal["chroma"]


# =============================================================================
# VectorStore 工厂方法
# =============================================================================

def get_vectorstore(
    collection_name: str,
    provider: Optional[VectorStoreProvider] = None,
    embeddings: Optional[Any] = None,
) -> VectorStore:
    """
    获取向量库实例 - 统一接口，一行代码切换向量库
    
    Args:
        collection_name: 集合/索引名称
        provider: 向量库提供商 (qdrant, chroma, pgvector)，默认从配置读取
        embeddings: Embeddings 实例，不指定则使用默认
    
    Returns:
        VectorStore: LangChain VectorStore 实例
    
    Raises:
        VectorStoreProviderError: 不支持的 provider 或依赖未安装
        VectorStoreConnectionError: 连接失败
    
    Example:
        >>> vs = get_vectorstore("code_chunks")
        >>> vs = get_vectorstore("docs", provider="chroma")
    """
    # 强制只允许使用 Chroma
    provider = provider or "chroma"
    embeddings = embeddings or get_embeddings()
    
    logger.debug(
        "creating_vectorstore",
        provider=provider,
        collection_name=collection_name,
    )
    
    if provider == "chroma":
        return _get_chroma_vectorstore(collection_name, embeddings)
    else:
        raise VectorStoreProviderError(
            f"Unsupported vectorstore provider: {provider}. "
            f"Supported providers: chroma"
        )


def _get_chroma_vectorstore(collection_name: str, embeddings) -> VectorStore:
    """获取 Chroma VectorStore"""
    try:
        from langchain_chroma import Chroma
    except ImportError:
        raise VectorStoreProviderError(
            "langchain-chroma is required for Chroma. "
            "Install with: pip install langchain-chroma"
        )
    
    logger.debug(
        "chroma_vectorstore_created",
        collection=collection_name,
        persist_dir=settings.chroma.persist_directory,
    )
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=settings.chroma.persist_directory,
    )




# =============================================================================
# 集合管理
# =============================================================================

async def create_collection_if_not_exists(
    collection_name: str,
    provider: Optional[VectorStoreProvider] = None,
    vector_size: int = 1536,
) -> bool:
    """
    创建向量集合（如果不存在）
    
    Args:
        collection_name: 集合名称
        provider: 向量库提供商
        vector_size: 向量维度（默认 OpenAI embedding 维度）
    
    Returns:
        bool: 是否创建了新集合
    
    Example:
        >>> created = await create_collection_if_not_exists("code_proj123", vector_size=1536)
    """
    provider = provider or "chroma"

    # Chroma 在首次使用时自动创建
    logger.debug("collection_auto_create", provider=provider, collection=collection_name)
    return False


def delete_collection(
    collection_name: str,
    provider: Optional[VectorStoreProvider] = None,
) -> bool:
    """
    删除向量集合
    
    Args:
        collection_name: 集合名称
        provider: 向量库提供商
    
    Returns:
        bool: 是否删除成功
    """
    provider = provider or "chroma"

    logger.warning(
        "collection_delete_not_implemented",
        provider=provider,
        collection=collection_name,
    )
    return False


def collection_exists(
    collection_name: str,
    provider: Optional[VectorStoreProvider] = None,
) -> bool:
    """
    检查集合是否存在
    
    Args:
        collection_name: 集合名称
        provider: 向量库提供商
    
    Returns:
        bool: 集合是否存在
    """
    provider = provider or "chroma"

    # Chroma 默认按需自动创建集合
    return True


def get_collection_info(
    collection_name: str,
    provider: Optional[VectorStoreProvider] = None,
) -> Optional[dict]:
    """
    获取集合信息
    
    Args:
        collection_name: 集合名称
        provider: 向量库提供商
    
    Returns:
        dict: 集合信息，包括向量数量等
    """
    provider = provider or "chroma"

    # 当前仅使用 Chroma，本地模式不提供集合统计信息
    logger.debug("collection_info_not_implemented", provider=provider, collection=collection_name)
    return None


# =============================================================================
# 便捷文档操作
# =============================================================================

async def add_documents_to_collection(
    collection_name: str,
    documents: List[Document],
    provider: Optional[VectorStoreProvider] = None,
    batch_size: int = 100,
) -> List[str]:
    """
    向集合添加文档
    
    Args:
        collection_name: 集合名称
        documents: 文档列表
        provider: 向量库提供商
        batch_size: 每批处理的文档数
    
    Returns:
        List[str]: 添加的文档 ID 列表
    """
    vectorstore = get_vectorstore(collection_name, provider=provider)
    
    all_ids: List[str] = []
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        logger.debug(
            "adding_documents_batch",
            collection=collection_name,
            batch_index=i // batch_size,
            batch_size=len(batch),
            total=len(documents),
        )
        
        ids = await vectorstore.aadd_documents(batch)
        all_ids.extend(ids)
    
    logger.info(
        "documents_added",
        collection=collection_name,
        count=len(all_ids),
    )
    return all_ids
