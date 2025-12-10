"""
LangChain 封装层

提供 LLM、Embedding、VectorStore、Retriever 的统一封装，
支持多种提供商的无缝切换。

模块结构：
- llm.py: LLM/ChatModel 工厂 (OpenAI, Anthropic, Ollama)
- embeddings.py: Embedding 模型工厂 (OpenAI, HuggingFace)
- vectorstore.py: 向量数据库工厂 (Qdrant, Chroma, PGVector)
- retrievers.py: Retriever 工厂 (Similarity, MMR, Compressed)
- prompts/: Prompt 模版 (代码讲解、问题生成、Tutor、分析文档)
- chains/: LangChain Chain (RAG、分析、多轮对话)
- exceptions.py: 自定义异常

使用示例：
    >>> from infrastructure.langchain import get_llm, get_embeddings, get_vectorstore
    >>> 
    >>> # 获取 LLM
    >>> llm = get_llm(provider="openai", model="gpt-4-turbo")
    >>> 
    >>> # 获取 Embedding
    >>> embeddings = get_embeddings()
    >>> 
    >>> # 获取向量存储
    >>> vectorstore = get_vectorstore("code_project_123")
    >>> 
    >>> # 获取 Retriever
    >>> from infrastructure.langchain.retrievers import get_code_retriever
    >>> retriever = get_code_retriever("project_123", search_type="mmr")
    >>> 
    >>> # 创建 RAG Chain
    >>> from infrastructure.langchain.chains import create_code_qa_chain
    >>> chain = create_code_qa_chain("project_123")
    >>> response = await chain.ainvoke("这个项目的入口在哪里？")
"""

# LLM
from .llm import (
    get_llm,
    get_cached_llm,
    LLMProvider,
)

# Embedding
from .embeddings import (
    get_embeddings,
    get_cached_embeddings,
    EmbeddingProvider,
)

# VectorStore
from .vectorstore import (
    get_vectorstore,
    create_collection_if_not_exists,
    VectorStoreProvider,
)

# Retriever
from .retrievers import (
    get_code_retriever,
    get_compressed_retriever,
    get_multi_query_retriever,
    SearchType,
)

# Chains
from .chains import (
    create_rag_chain,
    create_code_qa_chain,
    create_rag_chain_with_sources,
    create_analysis_chain,
    create_conversational_rag_chain,
    stream_rag_response,
    answer_code_question,
    generate_project_analysis,
)

# Exceptions
from .exceptions import (
    LangChainError,
    LLMError,
    EmbeddingError,
    VectorStoreError,
    RetrieverError,
    ChainError,
)

__all__ = [
    # LLM
    "get_llm",
    "get_cached_llm",
    "LLMProvider",
    # Embedding
    "get_embeddings",
    "get_cached_embeddings",
    "EmbeddingProvider",
    # VectorStore
    "get_vectorstore",
    "create_collection_if_not_exists",
    "VectorStoreProvider",
    # Retriever
    "get_code_retriever",
    "get_compressed_retriever",
    "get_multi_query_retriever",
    "SearchType",
    # Chains
    "create_rag_chain",
    "create_code_qa_chain",
    "create_rag_chain_with_sources",
    "create_analysis_chain",
    "create_conversational_rag_chain",
    "stream_rag_response",
    "answer_code_question",
    "generate_project_analysis",
    # Exceptions
    "LangChainError",
    "LLMError",
    "EmbeddingError",
    "VectorStoreError",
    "RetrieverError",
    "ChainError",
]

