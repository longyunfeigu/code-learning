"""
LangChain 封装层自定义异常

定义 LLM、Embedding、VectorStore 相关的异常类型。
"""

from typing import Optional, Any, Dict


class LangChainError(Exception):
    """LangChain 封装层基础异常"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.details = details or {}
        super().__init__(message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


# =============================================================================
# LLM 异常
# =============================================================================

class LLMError(LangChainError):
    """LLM 相关异常基类"""
    pass


class LLMProviderError(LLMError):
    """
    LLM 提供商错误
    
    当指定的 provider 不支持或模块未安装时抛出。
    """
    pass


class LLMConfigError(LLMError):
    """
    LLM 配置错误
    
    当缺少必要配置（如 API Key）时抛出。
    """
    pass


class LLMInvokeError(LLMError):
    """
    LLM 调用错误
    
    当 LLM API 调用失败时抛出。
    """
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {
            "provider": provider,
            "model": model,
        }
        if original_error:
            details["original_error"] = str(original_error)
        
        super().__init__(message, details)
        self.provider = provider
        self.model = model
        self.original_error = original_error


# =============================================================================
# Embedding 异常
# =============================================================================

class EmbeddingError(LangChainError):
    """Embedding 相关异常基类"""
    pass


class EmbeddingProviderError(EmbeddingError):
    """
    Embedding 提供商错误
    
    当指定的 provider 不支持或模块未安装时抛出。
    """
    pass


class EmbeddingConfigError(EmbeddingError):
    """
    Embedding 配置错误
    
    当缺少必要配置时抛出。
    """
    pass


# =============================================================================
# VectorStore 异常
# =============================================================================

class VectorStoreError(LangChainError):
    """VectorStore 相关异常基类"""
    pass


class VectorStoreProviderError(VectorStoreError):
    """
    VectorStore 提供商错误
    
    当指定的 provider 不支持或模块未安装时抛出。
    """
    pass


class VectorStoreConnectionError(VectorStoreError):
    """
    VectorStore 连接错误
    
    当无法连接到向量数据库时抛出。
    """
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        url: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {
            "provider": provider,
            "url": url,
        }
        if original_error:
            details["original_error"] = str(original_error)
        
        super().__init__(message, details)
        self.provider = provider
        self.url = url
        self.original_error = original_error


class CollectionNotFoundError(VectorStoreError):
    """
    集合不存在错误
    
    当指定的向量集合不存在时抛出。
    """
    
    def __init__(self, collection_name: str, provider: Optional[str] = None):
        message = f"Collection '{collection_name}' not found"
        details = {
            "collection_name": collection_name,
            "provider": provider,
        }
        super().__init__(message, details)
        self.collection_name = collection_name


# =============================================================================
# Retriever 异常
# =============================================================================

class RetrieverError(LangChainError):
    """Retriever 相关异常基类"""
    pass


class RetrievalError(RetrieverError):
    """
    检索错误
    
    当检索过程中发生错误时抛出。
    """
    
    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {}
        if query:
            details["query"] = query[:100]  # 截断长查询
        if original_error:
            details["original_error"] = str(original_error)
        
        super().__init__(message, details)
        self.query = query
        self.original_error = original_error


# =============================================================================
# Chain 异常
# =============================================================================

class ChainError(LangChainError):
    """Chain 相关异常基类"""
    pass


# RAGChainError 作为 ChainError 的别名保持兼容
RAGChainError = ChainError


class ChainConfigError(ChainError):
    """Chain 配置错误"""
    pass


# RAGConfigError 作为 ChainConfigError 的别名
RAGConfigError = ChainConfigError


class ChainInvokeError(ChainError):
    """Chain 调用错误"""
    
    def __init__(
        self,
        message: str,
        question: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {}
        if question:
            details["question"] = question[:200]
        if original_error:
            details["original_error"] = str(original_error)
        
        super().__init__(message, details)
        self.question = question
        self.original_error = original_error


# RAGInvokeError 作为 ChainInvokeError 的别名
RAGInvokeError = ChainInvokeError
