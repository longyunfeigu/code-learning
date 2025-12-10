"""
Retriever 配置模块 - RAG 检索组件

提供多种检索策略：
- 基础语义检索 (similarity)
- MMR (Maximal Marginal Relevance) - 平衡相关性和多样性
- 相似度阈值检索 (similarity_score_threshold)
- 上下文压缩检索 (contextual compression)
- 多查询检索 (multi-query)

使用示例:
    >>> from infrastructure.langchain.retrievers import get_code_retriever
    >>> retriever = get_code_retriever("proj_123", search_type="mmr")
    >>> docs = await retriever.ainvoke("项目入口在哪里？")
"""

from typing import Optional, Literal, List, Any

from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document

from core.config import settings
from core.logging_config import get_logger
from .llm import get_llm
from .vectorstore import get_vectorstore
from .exceptions import RetrieverError, RetrievalError

logger = get_logger(__name__)

# 检索策略类型
SearchType = Literal["similarity", "mmr", "similarity_score_threshold"]


def get_code_retriever(
    project_id: str,
    search_k: int = 10,
    search_type: SearchType = "mmr",
    score_threshold: Optional[float] = None,
    fetch_k: Optional[int] = None,
    lambda_mult: float = 0.5,
) -> BaseRetriever:
    """
    获取代码检索器
    
    Args:
        project_id: 项目 ID，用于确定集合名称
        search_k: 返回文档数量
        search_type: 检索策略
            - "similarity": 纯相似度检索
            - "mmr": 最大边际相关性，平衡相关性和多样性
            - "similarity_score_threshold": 带相似度阈值的检索
        score_threshold: 相似度阈值（仅 similarity_score_threshold 生效）
        fetch_k: MMR 初始检索数量（默认为 search_k * 2）
        lambda_mult: MMR 多样性参数 (0=最大多样性, 1=最大相关性)
    
    Returns:
        BaseRetriever: LangChain Retriever 实例
    
    Example:
        >>> retriever = get_code_retriever("proj_123")
        >>> retriever = get_code_retriever("proj_123", search_type="mmr", search_k=20)
        >>> retriever = get_code_retriever("proj_123", search_type="similarity_score_threshold", score_threshold=0.7)
    """
    collection_name = f"code_{project_id}"
    vectorstore = get_vectorstore(collection_name)
    
    search_kwargs: dict[str, Any] = {"k": search_k}
    
    if search_type == "mmr":
        search_kwargs["fetch_k"] = fetch_k or search_k * 2
        search_kwargs["lambda_mult"] = lambda_mult
    
    if search_type == "similarity_score_threshold":
        if score_threshold is None:
            score_threshold = 0.5  # 默认阈值
        search_kwargs["score_threshold"] = score_threshold
    
    retriever = vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs=search_kwargs,
    )
    
    logger.debug(
        "created_code_retriever",
        collection=collection_name,
        search_type=search_type,
        search_k=search_k,
        **({k: v for k, v in search_kwargs.items() if k != "k"}),
    )
    
    return retriever


def get_document_retriever(
    collection_name: str,
    search_k: int = 5,
    search_type: SearchType = "similarity",
) -> BaseRetriever:
    """
    获取通用文档检索器
    
    Args:
        collection_name: 集合名称
        search_k: 返回文档数量
        search_type: 检索策略
    
    Returns:
        BaseRetriever: Retriever 实例
    """
    vectorstore = get_vectorstore(collection_name)
    
    search_kwargs: dict[str, Any] = {"k": search_k}
    
    if search_type == "mmr":
        search_kwargs["fetch_k"] = search_k * 2
    
    logger.debug(
        "created_document_retriever",
        collection=collection_name,
        search_type=search_type,
        search_k=search_k,
    )
    
    return vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs=search_kwargs,
    )


# =============================================================================
# 高级检索器
# =============================================================================

def get_compressed_retriever(
    project_id: str,
    search_k: int = 10,
    use_llm_filter: bool = False,
) -> BaseRetriever:
    """
    获取带上下文压缩的检索器
    
    使用 LLM 对检索结果进行筛选和压缩，
    只保留与查询最相关的内容。
    
    Args:
        project_id: 项目 ID
        search_k: 返回文档数量（会先检索 2x 再压缩）
        use_llm_filter: 是否使用 LLM 过滤
    
    Returns:
        BaseRetriever: 带压缩功能的 Retriever
    
    Note:
        LLM 过滤会增加延迟和成本，建议仅在需要高精度时使用。
    """
    # 基础检索器检索更多文档，压缩后返回 search_k 个
    base_retriever = get_code_retriever(project_id, search_k=search_k * 2)
    
    if not use_llm_filter:
        return base_retriever
    
    try:
        from langchain.retrievers import ContextualCompressionRetriever
        from langchain.retrievers.document_compressors import LLMChainExtractor
    except ImportError:
        logger.warning(
            "compression_retriever_not_available",
            reason="langchain package required for ContextualCompressionRetriever",
        )
        return base_retriever
    
    llm = get_llm()
    compressor = LLMChainExtractor.from_llm(llm)
    
    logger.debug(
        "created_compressed_retriever",
        project_id=project_id,
        search_k=search_k,
        use_llm_filter=True,
    )
    
    return ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever,
    )


def get_multi_query_retriever(
    project_id: str,
    search_k: int = 5,
) -> BaseRetriever:
    """
    获取多查询检索器
    
    使用 LLM 生成多个相关查询，然后合并所有查询的结果。
    适用于模糊或复杂的查询场景。
    
    Args:
        project_id: 项目 ID
        search_k: 每个查询返回的文档数量
    
    Returns:
        BaseRetriever: 多查询 Retriever
    
    Note:
        会调用 LLM 生成查询变体，增加延迟和成本。
    """
    base_retriever = get_code_retriever(project_id, search_k=search_k)
    
    try:
        from langchain.retrievers.multi_query import MultiQueryRetriever
    except ImportError:
        logger.warning(
            "multi_query_retriever_not_available",
            reason="langchain package required for MultiQueryRetriever",
        )
        return base_retriever
    
    llm = get_llm()
    
    logger.debug(
        "created_multi_query_retriever",
        project_id=project_id,
        search_k=search_k,
    )
    
    return MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm,
    )


def get_ensemble_retriever(
    project_id: str,
    search_k: int = 10,
    bm25_weight: float = 0.5,
) -> BaseRetriever:
    """
    获取集成检索器（向量 + BM25）
    
    结合语义检索和关键词检索，提高召回率。
    
    Args:
        project_id: 项目 ID
        search_k: 返回文档数量
        bm25_weight: BM25 检索权重 (0-1)
    
    Returns:
        BaseRetriever: 集成 Retriever
    
    Note:
        需要额外存储 BM25 索引，暂不实现。
    """
    # TODO: 实现 BM25 + 向量的集成检索
    logger.warning(
        "ensemble_retriever_not_implemented",
        message="Falling back to standard retriever",
    )
    return get_code_retriever(project_id, search_k=search_k)


# =============================================================================
# 检索工具函数
# =============================================================================

async def retrieve_code_chunks(
    project_id: str,
    query: str,
    search_k: int = 10,
    search_type: SearchType = "mmr",
) -> List[Document]:
    """
    检索代码片段的便捷函数
    
    Args:
        project_id: 项目 ID
        query: 查询文本
        search_k: 返回文档数量
        search_type: 检索策略
    
    Returns:
        List[Document]: 检索到的文档列表
    
    Example:
        >>> docs = await retrieve_code_chunks("proj_123", "用户认证逻辑")
    """
    try:
        retriever = get_code_retriever(
            project_id=project_id,
            search_k=search_k,
            search_type=search_type,
        )
        
        documents = await retriever.ainvoke(query)
        
        logger.debug(
            "code_chunks_retrieved",
            project_id=project_id,
            query=query[:50],
            count=len(documents),
        )
        
        return documents
    
    except Exception as e:
        logger.error(
            "retrieval_failed",
            project_id=project_id,
            query=query[:50],
            error=str(e),
        )
        raise RetrievalError(
            message=f"Failed to retrieve code chunks: {e}",
            query=query,
            original_error=e,
        )


def format_retrieved_documents(
    documents: List[Document],
    include_metadata: bool = True,
) -> str:
    """
    格式化检索到的文档
    
    Args:
        documents: 文档列表
        include_metadata: 是否包含元数据（文件路径、行号等）
    
    Returns:
        str: 格式化后的文本
    """
    formatted = []
    
    for i, doc in enumerate(documents, 1):
        if include_metadata:
            source = doc.metadata.get("source", "unknown")
            start_line = doc.metadata.get("start_line", "?")
            end_line = doc.metadata.get("end_line", "?")
            language = doc.metadata.get("language", "")
            
            header = f"## [{i}] {source} (L{start_line}-{end_line})"
            code_block = f"```{language}\n{doc.page_content}\n```"
            formatted.append(f"{header}\n{code_block}")
        else:
            formatted.append(f"## [{i}]\n```\n{doc.page_content}\n```")
    
    return "\n\n".join(formatted)
