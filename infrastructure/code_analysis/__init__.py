"""代码分析服务模块.

提供代码解析、索引和搜索能力：
- :mod:`git_service` - Git 仓库克隆与管理
- :mod:`tree_sitter_parser` - Tree-sitter AST 解析器
- :mod:`code_indexer` - 代码向量索引服务
- :mod:`symbol_search` - 符号搜索服务
"""

from .git_service import GitService, GitCloneError, GitOperationError, RepoInfo
from .tree_sitter_parser import (
    TreeSitterParser,
    CodeSymbol,
    SymbolKind,
    FileSymbols,
    ProjectSymbols,
    parser,
)
from .code_indexer import CodeIndexer, CodeChunk, IndexingResult
from .symbol_search import SymbolSearchService, SearchResult

__all__ = [
    "GitService",
    "GitCloneError",
    "GitOperationError",
    "RepoInfo",
    "TreeSitterParser",
    "CodeSymbol",
    "SymbolKind",
    "FileSymbols",
    "ProjectSymbols",
    "parser",
    "CodeIndexer",
    "CodeChunk",
    "IndexingResult",
    "SymbolSearchService",
    "SearchResult",
]
