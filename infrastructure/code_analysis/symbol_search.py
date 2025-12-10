"""符号搜索与索引服务.

基于 :mod:`tree_sitter_parser` 提取的符号，提供结构化搜索能力：
- 按名称搜索，支持精确/模糊匹配
- 按符号类型和文件路径过滤
- 返回符号定义以及源码片段
"""

from typing import Optional, List, Dict
from dataclasses import dataclass
from pathlib import Path

from core.config import settings
from core.logging_config import get_logger
from .tree_sitter_parser import CodeSymbol, SymbolKind, FileSymbols, ProjectSymbols, parser

logger = get_logger(__name__)


@dataclass
class SearchResult:
    """符号搜索结果."""

    symbol: CodeSymbol
    score: float
    context: Optional[str] = None  # 源码片段或周边上下文


class SymbolSearchService:
    """
    符号搜索服务

    支持：
    - 按名称搜索符号
    - 按类型过滤
    - 模糊匹配
    """

    def __init__(self, project_id: str) -> None:
        """初始化搜索服务.

        Args:
            project_id: 项目 ID
        """
        self.project_id = project_id
        # project_id -> CodeSymbol 列表
        self._symbol_cache: Dict[str, List[CodeSymbol]] = {}

    async def search(
        self,
        query: str,
        kinds: Optional[List[SymbolKind]] = None,
        file_filter: Optional[str] = None,
        limit: int = 20,
        fuzzy: bool = True,
    ) -> List[SearchResult]:
        """
        搜索符号

        Args:
            query: 搜索查询
            kinds: 符号类型过滤
            file_filter: 文件路径过滤（支持通配符）
            limit: 返回结果数量限制
            fuzzy: 是否模糊匹配

        Returns:
            List[SearchResult]: 搜索结果列表
        """
        results: List[SearchResult] = []

        # 获取所有符号（通常由 index_repository 预先填充）
        symbols = await self._get_all_symbols()

        for symbol in symbols:
            # 类型过滤
            if kinds and symbol.kind not in kinds:
                continue

            # 文件过滤
            if file_filter and not self._match_path(symbol.file_path, file_filter):
                continue

            # 名称匹配
            score = self._calculate_match_score(query, symbol.name, fuzzy)

            if score > 0:
                results.append(
                    SearchResult(
                        symbol=symbol,
                        score=score,
                    )
                )

        results.sort(key=lambda x: x.score, reverse=True)

        return results[:limit]

    async def find_references(
        self,
        symbol_name: str,
        file_path: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        查找符号引用

        Args:
            symbol_name: 符号名称
            file_path: 限定在特定文件中搜索

        Returns:
            List[SearchResult]: 引用位置列表
        """
        # TODO: 实现引用查找（需要更完整的 AST 使用关系分析）
        return []

    async def find_definitions(
        self,
        symbol_name: str,
    ) -> List[SearchResult]:
        """
        查找符号定义

        Args:
            symbol_name: 符号名称

        Returns:
            List[SearchResult]: 定义位置列表
        """
        return await self.search(
            query=symbol_name,
            fuzzy=False,
            limit=10,
        )

    async def get_symbol_hierarchy(
        self,
        file_path: str,
    ) -> List[CodeSymbol]:
        """
        获取文件的符号层次结构

        Args:
            file_path: 文件路径

        Returns:
            List[CodeSymbol]: 顶层符号列表（包含子符号）
        """
        symbols = await self._get_file_symbols(file_path)

        return [s for s in symbols if s.parent is None]

    async def index_repository(
        self,
        repo_path: str,
        file_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> ProjectSymbols:
        """解析整个仓库并构建符号索引.

        该方法会：
        1. 按文件模式收集源码文件
        2. 通过 Tree-sitter 解析每个文件的符号
        3. 将结果缓存到内存，供后续搜索使用
        """

        root = Path(repo_path)
        if not root.exists():
            logger.warning("repo_path_not_exists", repo_path=repo_path)
            return ProjectSymbols(project_id=self.project_id, files=[])

        file_patterns = file_patterns or ["*.py", "*.ts", "*.tsx", "*.js"]
        exclude_patterns = exclude_patterns or [
            "*/.git/*",
            "*/node_modules/*",
            "*/__pycache__/*",
        ]

        files: List[Path] = []
        for pattern in file_patterns:
            files.extend(root.rglob(pattern))

        file_symbol_list: List[FileSymbols] = []
        all_symbols: List[CodeSymbol] = []

        max_file_size = settings.code_analysis.max_file_size

        for path in files:
            rel_path = str(path.relative_to(root))

            # 排除大文件
            try:
                if path.stat().st_size > max_file_size:
                    logger.debug(
                        "symbol_index_skip_large_file",
                        file=rel_path,
                        size=path.stat().st_size,
                        max_size=max_file_size,
                    )
                    continue
            except OSError:
                continue

            if any(self._match_path(rel_path, patt) for patt in exclude_patterns):
                continue

            symbols = await parser.parse_file(str(path))
            if not symbols:
                continue

            # 统一使用仓库相对路径，便于前端展示和测试
            for sym in symbols:
                sym.file_path = rel_path

            file_symbols = FileSymbols(file_path=rel_path, symbols=symbols)
            file_symbol_list.append(file_symbols)
            all_symbols.extend(symbols)

        await self.cache_symbols(all_symbols)

        logger.info(
            "symbol_index_completed",
            project_id=self.project_id,
            files=len(file_symbol_list),
            symbols=len(all_symbols),
        )

        return ProjectSymbols(project_id=self.project_id, files=file_symbol_list)

    async def _get_all_symbols(self) -> List[CodeSymbol]:
        """获取项目所有符号（从缓存或数据库）"""
        if self.project_id in self._symbol_cache:
            return self._symbol_cache[self.project_id]

        # 目前仅使用内存缓存，后续可以扩展为从数据库加载
        return []

    async def _get_file_symbols(self, file_path: str) -> List[CodeSymbol]:
        """获取指定文件的符号"""
        all_symbols = await self._get_all_symbols()
        return [s for s in all_symbols if s.file_path == file_path]

    def _match_path(self, path: str, pattern: str) -> bool:
        """检查路径是否匹配模式"""
        import fnmatch

        return fnmatch.fnmatch(path, pattern)

    def _calculate_match_score(
        self,
        query: str,
        target: str,
        fuzzy: bool,
    ) -> float:
        """
        计算匹配分数

        Args:
            query: 查询字符串
            target: 目标字符串
            fuzzy: 是否模糊匹配

        Returns:
            float: 匹配分数 (0-1)
        """
        query_lower = query.lower()
        target_lower = target.lower()

        # 完全匹配
        if query_lower == target_lower:
            return 1.0

        # 前缀匹配
        if target_lower.startswith(query_lower):
            return 0.9

        # 包含匹配
        if query_lower in target_lower:
            return 0.7

        # 模糊匹配
        if fuzzy:
            # 简单的子序列匹配
            score = self._subsequence_match(query_lower, target_lower)
            if score > 0.5:
                return score * 0.6

        return 0.0

    def _subsequence_match(self, query: str, target: str) -> float:
        """子序列匹配分数"""
        if not query:
            return 1.0
        if not target:
            return 0.0

        query_idx = 0
        matches = 0

        for char in target:
            if query_idx < len(query) and char == query[query_idx]:
                matches += 1
                query_idx += 1

        if query_idx == len(query):
            return matches / len(target)

        return 0.0

    async def cache_symbols(self, symbols: List[CodeSymbol]) -> None:
        """缓存符号列表"""
        self._symbol_cache[self.project_id] = symbols

    def clear_cache(self) -> None:
        """清除缓存"""
        if self.project_id in self._symbol_cache:
            del self._symbol_cache[self.project_id]
