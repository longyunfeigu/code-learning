"""
RAG 检索中间件 - 代码检索增强

职责：
- 语义检索代码片段
- 符号搜索补充
- 上下文压缩和筛选
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CodeChunk:
    """代码片段数据类"""
    content: str
    file_path: str
    start_line: int
    end_line: int
    language: str
    score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class RetrievalResult:
    """检索结果数据类"""
    chunks: List[CodeChunk]
    query: str
    total_found: int
    search_type: str  # "semantic", "symbol", "hybrid"


class RAGMiddleware:
    """
    RAG 检索中间件
    
    在 Agent 执行过程中提供代码检索能力，
    支持语义检索和符号搜索的混合模式。
    """
    
    def __init__(
        self,
        project_id: str,
        vector_store: Optional[Any] = None,  # LangChain VectorStore
        code_search: Optional[Any] = None,   # CodeSearchService
    ):
        self.project_id = project_id
        self.vector_store = vector_store
        self.code_search = code_search
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        search_type: str = "hybrid",
        file_filter: Optional[List[str]] = None,
        language_filter: Optional[List[str]] = None,
    ) -> RetrievalResult:
        """
        检索代码片段
        
        Args:
            query: 检索查询
            top_k: 返回结果数量
            search_type: 搜索类型 (semantic/symbol/hybrid)
            file_filter: 文件路径过滤
            language_filter: 语言过滤
        
        Returns:
            RetrievalResult 检索结果
        """
        chunks: List[CodeChunk] = []
        
        if search_type in ("semantic", "hybrid") and self.vector_store:
            semantic_results = await self._semantic_search(
                query, top_k, file_filter, language_filter
            )
            chunks.extend(semantic_results)
        
        if search_type in ("symbol", "hybrid") and self.code_search:
            symbol_results = await self._symbol_search(
                query, top_k, file_filter, language_filter
            )
            # 去重并合并
            existing_paths = {(c.file_path, c.start_line) for c in chunks}
            for chunk in symbol_results:
                if (chunk.file_path, chunk.start_line) not in existing_paths:
                    chunks.append(chunk)
        
        # 按相关度排序
        chunks.sort(key=lambda x: x.score, reverse=True)
        chunks = chunks[:top_k]
        
        return RetrievalResult(
            chunks=chunks,
            query=query,
            total_found=len(chunks),
            search_type=search_type,
        )
    
    async def _semantic_search(
        self,
        query: str,
        top_k: int,
        file_filter: Optional[List[str]] = None,
        language_filter: Optional[List[str]] = None,
    ) -> List[CodeChunk]:
        """语义向量检索"""
        if not self.vector_store:
            return []
        
        # TODO: 实现向量检索逻辑
        # 使用 LangChain VectorStore.similarity_search_with_score
        return []
    
    async def _symbol_search(
        self,
        query: str,
        top_k: int,
        file_filter: Optional[List[str]] = None,
        language_filter: Optional[List[str]] = None,
    ) -> List[CodeChunk]:
        """符号搜索"""
        if not self.code_search:
            return []
        
        # TODO: 实现符号搜索逻辑
        # 使用 CodeSearchService.search_symbols
        return []
    
    def format_context(
        self,
        chunks: List[CodeChunk],
        max_tokens: int = 4000,
    ) -> str:
        """
        格式化检索结果为上下文字符串
        
        Args:
            chunks: 代码片段列表
            max_tokens: 最大 token 数（近似）
        
        Returns:
            格式化的上下文字符串
        """
        context_parts = []
        current_length = 0
        
        for chunk in chunks:
            chunk_text = f"""
## {chunk.file_path} (L{chunk.start_line}-{chunk.end_line})

```{chunk.language}
{chunk.content}
```
"""
            chunk_length = len(chunk_text) // 4  # 粗略估算 token 数
            
            if current_length + chunk_length > max_tokens:
                break
            
            context_parts.append(chunk_text)
            current_length += chunk_length
        
        return "\n".join(context_parts)

