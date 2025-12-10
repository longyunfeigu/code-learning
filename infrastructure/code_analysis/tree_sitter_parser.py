"""
Tree-sitter AST 解析器

提供多语言的 AST 解析能力，用于提取代码符号。
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

from core.logging_config import get_logger

logger = get_logger(__name__)


class SymbolKind(Enum):
    """符号类型"""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    PROPERTY = "property"
    VARIABLE = "variable"
    CONSTANT = "constant"
    INTERFACE = "interface"
    ENUM = "enum"
    IMPORT = "import"


@dataclass
class CodeSymbol:
    """代码符号"""
    name: str
    kind: SymbolKind
    file_path: str
    start_line: int
    end_line: int
    start_col: int = 0
    end_col: int = 0
    signature: Optional[str] = None
    docstring: Optional[str] = None
    parent: Optional[str] = None
    children: List["CodeSymbol"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TreeSitterParser:
    """
    Tree-sitter AST 解析器
    
    支持的语言：
    - Python
    - TypeScript/JavaScript
    - Java
    - Go
    - Rust
    """
    
    # 语言到文件扩展名的映射
    LANGUAGE_EXTENSIONS = {
        "python": [".py", ".pyi"],
        "typescript": [".ts", ".tsx"],
        "javascript": [".js", ".jsx", ".mjs"],
        "java": [".java"],
        "go": [".go"],
        "rust": [".rs"],
    }
    
    def __init__(self):
        """初始化解析器"""
        self._parsers: Dict[str, Any] = {}
        self._initialized = False
    
    def _ensure_initialized(self, language: str) -> bool:
        """
        确保指定语言的解析器已初始化
        
        Returns:
            bool: 是否成功初始化
        """
        if language in self._parsers:
            return True
        
        try:
            import tree_sitter_python
            import tree_sitter_javascript
            from tree_sitter import Language, Parser
        except ImportError:
            logger.warning(
                "tree_sitter_not_available",
                reason="tree-sitter packages not installed",
            )
            return False
        
        # 根据语言加载解析器
        language_modules = {
            "python": ("tree_sitter_python", tree_sitter_python),
            "javascript": ("tree_sitter_javascript", tree_sitter_javascript),
            "typescript": ("tree_sitter_javascript", tree_sitter_javascript),
        }
        
        if language not in language_modules:
            logger.warning("unsupported_language", language=language)
            return False
        
        module_name, module = language_modules[language]
        
        try:
            parser = Parser()
            parser.language = Language(module.language())
            self._parsers[language] = parser
            return True
        except Exception as e:
            logger.error("parser_init_failed", language=language, error=str(e))
            return False
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """
        根据文件扩展名检测语言
        
        Args:
            file_path: 文件路径
        
        Returns:
            str: 语言名称，未知则返回 None
        """
        ext = Path(file_path).suffix.lower()
        
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                return lang
        
        return None
    
    async def parse_file(
        self,
        file_path: str,
        content: Optional[str] = None,
    ) -> List[CodeSymbol]:
        """
        解析文件，提取符号
        
        Args:
            file_path: 文件路径
            content: 文件内容，不提供则从路径读取
        
        Returns:
            List[CodeSymbol]: 提取的符号列表
        """
        language = self.detect_language(file_path)
        
        if not language:
            logger.debug("unknown_language", file=file_path)
            return []
        
        if not self._ensure_initialized(language):
            return []
        
        # 读取文件内容
        if content is None:
            try:
                content = Path(file_path).read_text(encoding="utf-8")
            except Exception as e:
                logger.warning("file_read_failed", file=file_path, error=str(e))
                return []
        
        # 解析
        parser = self._parsers[language]
        tree = parser.parse(bytes(content, "utf-8"))
        
        # 提取符号
        symbols = self._extract_symbols(tree.root_node, file_path, language, content)
        
        logger.debug(
            "file_parsed",
            file=file_path,
            language=language,
            symbols_count=len(symbols),
        )
        
        return symbols
    
    def _extract_symbols(
        self,
        node: Any,
        file_path: str,
        language: str,
        content: str,
        parent: Optional[str] = None,
    ) -> List[CodeSymbol]:
        """从 AST 节点提取符号"""
        symbols = []
        
        # 根据语言和节点类型提取符号
        if language == "python":
            symbols = self._extract_python_symbols(node, file_path, content, parent)
        elif language in ("javascript", "typescript"):
            symbols = self._extract_js_symbols(node, file_path, content, parent)
        
        return symbols
    
    def _extract_python_symbols(
        self,
        node: Any,
        file_path: str,
        content: str,
        parent: Optional[str] = None,
    ) -> List[CodeSymbol]:
        """提取 Python 符号"""
        symbols = []
        
        for child in node.children:
            symbol = None
            
            if child.type == "class_definition":
                name_node = child.child_by_field_name("name")
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    symbol = CodeSymbol(
                        name=name,
                        kind=SymbolKind.CLASS,
                        file_path=file_path,
                        start_line=child.start_point[0] + 1,
                        end_line=child.end_point[0] + 1,
                        parent=parent,
                    )
                    # 递归提取类内部的方法
                    body = child.child_by_field_name("body")
                    if body:
                        symbol.children = self._extract_python_symbols(
                            body, file_path, content, name
                        )
            
            elif child.type == "function_definition":
                name_node = child.child_by_field_name("name")
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    kind = SymbolKind.METHOD if parent else SymbolKind.FUNCTION
                    symbol = CodeSymbol(
                        name=name,
                        kind=kind,
                        file_path=file_path,
                        start_line=child.start_point[0] + 1,
                        end_line=child.end_point[0] + 1,
                        parent=parent,
                    )
            
            if symbol:
                symbols.append(symbol)
            
            # 递归处理子节点
            if child.type not in ("class_definition", "function_definition"):
                symbols.extend(
                    self._extract_python_symbols(child, file_path, content, parent)
                )
        
        return symbols
    
    def _extract_js_symbols(
        self,
        node: Any,
        file_path: str,
        content: str,
        parent: Optional[str] = None,
    ) -> List[CodeSymbol]:
        """提取 JavaScript/TypeScript 符号"""
        symbols = []
        
        for child in node.children:
            symbol = None
            
            if child.type == "class_declaration":
                name_node = child.child_by_field_name("name")
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    symbol = CodeSymbol(
                        name=name,
                        kind=SymbolKind.CLASS,
                        file_path=file_path,
                        start_line=child.start_point[0] + 1,
                        end_line=child.end_point[0] + 1,
                        parent=parent,
                    )
            
            elif child.type in ("function_declaration", "method_definition"):
                name_node = child.child_by_field_name("name")
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    kind = SymbolKind.METHOD if parent else SymbolKind.FUNCTION
                    symbol = CodeSymbol(
                        name=name,
                        kind=kind,
                        file_path=file_path,
                        start_line=child.start_point[0] + 1,
                        end_line=child.end_point[0] + 1,
                        parent=parent,
                    )
            
            if symbol:
                symbols.append(symbol)
            
            # 递归
            symbols.extend(
                self._extract_js_symbols(child, file_path, content, parent)
            )
        
        return symbols


# 全局解析器实例
parser = TreeSitterParser()

