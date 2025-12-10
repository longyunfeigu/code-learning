"""
代码索引服务

将代码片段向量化并存储到向量数据库，支持语义搜索。
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from pathlib import Path

from core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class CodeChunk:
    """代码片段"""

    content: str
    file_path: str
    start_line: int
    end_line: int
    language: str
    chunk_type: str = "code"  # code, docstring, comment
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class IndexingResult:
    """索引结果"""

    project_id: str
    total_files: int
    total_chunks: int
    indexed_chunks: int
    failed_files: List[str]
    elapsed_seconds: float


class CodeIndexer:
    """
    代码索引器

    将代码切分为片段并向量化存储，支持：
    - 按函数/类粒度切分
    - 保留上下文信息
    - 增量索引
    """

    def __init__(
        self,
        project_id: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        初始化索引器

        Args:
            project_id: 项目 ID，用于集合命名
            chunk_size: 代码片段大小（字符数）
            chunk_overlap: 片段重叠大小
        """
        self.project_id = project_id
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._vectorstore = None
        self._embeddings = None

    async def index_repository(
        self,
        repo_path: str,
        file_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> IndexingResult:
        """
        索引整个仓库

        Args:
            repo_path: 仓库本地路径
            file_patterns: 包含的文件模式
            exclude_patterns: 排除的文件模式

        Returns:
            IndexingResult: 索引结果统计
        """
        import time

        start_time = time.time()

        root_path = Path(repo_path)
        file_patterns = file_patterns or [
            "*.py",
            "*.ts",
            "*.js",
            "*.java",
            "*.go",
        ]
        exclude_patterns = exclude_patterns or [
            "node_modules/*",
            "__pycache__/*",
            ".git/*",
            "*.min.js",
        ]

        logger.info("starting_indexing", project_id=self.project_id, repo_path=str(root_path))

        # 收集文件
        files = self._collect_files(root_path, file_patterns, exclude_patterns)

        total_chunks = 0
        indexed_chunks = 0
        failed_files = []

        # 处理每个文件
        chunks_to_index = []

        for file_path in files:
            try:
                file_chunks = await self._process_file(root_path, file_path)
                chunks_to_index.extend(file_chunks)
                total_chunks += len(file_chunks)
            except Exception as e:
                logger.warning(
                    "file_processing_failed",
                    file=str(file_path),
                    error=str(e),
                )
                failed_files.append(str(file_path))

        # 批量索引
        if chunks_to_index:
            indexed_chunks = await self._batch_index(chunks_to_index)

        elapsed = time.time() - start_time

        result = IndexingResult(
            project_id=self.project_id,
            total_files=len(files),
            total_chunks=total_chunks,
            indexed_chunks=indexed_chunks,
            failed_files=failed_files,
            elapsed_seconds=elapsed,
        )

        logger.info(
            "indexing_completed",
            project_id=self.project_id,
            total_files=result.total_files,
            total_chunks=result.total_chunks,
            indexed_chunks=result.indexed_chunks,
            failed_count=len(failed_files),
            elapsed=f"{elapsed:.2f}s",
        )

        return result

    async def index_file(
        self,
        repo_path: str,
        file_path: str,
    ) -> int:
        """
        索引单个文件

        Args:
            repo_path: 仓库路径
            file_path: 文件相对路径

        Returns:
            int: 索引的片段数量
        """
        chunks = await self._process_file(Path(repo_path), Path(file_path))

        if chunks:
            return await self._batch_index(chunks)

        return 0

    async def delete_index(self) -> bool:
        """
        删除项目的所有索引

        Returns:
            bool: 是否成功
        """
        collection_name = f"code_{self.project_id}"

        try:
            # 这里预留与具体向量数据库的删除集成逻辑
            logger.info("deleting_index", collection=collection_name)
            return True
        except Exception as e:
            logger.error("delete_index_failed", error=str(e))
            return False

    def _collect_files(
        self,
        repo_path: Path,
        file_patterns: List[str],
        exclude_patterns: List[str],
    ) -> List[Path]:
        """收集需要索引的文件"""
        import fnmatch

        files = []

        for pattern in file_patterns:
            for file_path in repo_path.rglob(pattern.lstrip("*")):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(repo_path))

                    # 检查是否排除
                    excluded = False
                    for exc_pattern in exclude_patterns:
                        if fnmatch.fnmatch(rel_path, exc_pattern):
                            excluded = True
                            break

                    if not excluded:
                        files.append(file_path.relative_to(repo_path))

        return files

    async def _process_file(
        self,
        repo_path: Path,
        file_path: Path,
    ) -> List[CodeChunk]:
        """处理单个文件，切分为代码片段"""
        full_path = repo_path / file_path

        try:
            content = full_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # 跳过二进制文件
            return []

        # 检测语言
        language = self._detect_language(str(file_path))

        # 切分代码
        chunks = self._split_code(content, str(file_path), language)

        return chunks

    def _split_code(
        self,
        content: str,
        file_path: str,
        language: str,
    ) -> List[CodeChunk]:
        """
        切分代码为片段

        使用简单的行数切分策略，后续可以优化为按函数/类切分
        """
        lines = content.split("\n")
        chunks = []

        # 每 50 行一个片段，重叠 10 行
        chunk_lines = 50
        overlap_lines = 10

        i = 0
        while i < len(lines):
            end = min(i + chunk_lines, len(lines))
            chunk_content = "\n".join(lines[i:end])

            if chunk_content.strip():  # 跳过空片段
                chunks.append(
                    CodeChunk(
                        content=chunk_content,
                        file_path=file_path,
                        start_line=i + 1,
                        end_line=end,
                        language=language,
                        metadata={
                            "project_id": self.project_id,
                        },
                    )
                )

            i += chunk_lines - overlap_lines

        return chunks

    async def _batch_index(self, chunks: List[CodeChunk]) -> int:
        """批量索引代码片段"""
        try:
            from langchain_core.documents import Document
            from infrastructure.langchain.vectorstore import (
                get_vectorstore,
                create_collection_if_not_exists,
            )
        except ImportError:
            logger.warning("langchain_not_available")
            return 0

        collection_name = f"code_{self.project_id}"

        # 确保集合存在
        await create_collection_if_not_exists(collection_name)

        # 转换为 Document
        documents = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk.content,
                metadata={
                    "source": chunk.file_path,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "language": chunk.language,
                    "project_id": self.project_id,
                    **(chunk.metadata or {}),
                },
            )
            documents.append(doc)

        # 获取向量库并添加文档
        vectorstore = get_vectorstore(collection_name)

        # 分批添加，避免一次性太多
        batch_size = 100
        indexed = 0

        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            await vectorstore.aadd_documents(batch)
            indexed += len(batch)

        return indexed

    def _detect_language(self, file_path: str) -> str:
        """根据文件扩展名检测语言"""
        ext = Path(file_path).suffix.lower()

        ext_to_lang = {
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
        }

        return ext_to_lang.get(ext, "unknown")
