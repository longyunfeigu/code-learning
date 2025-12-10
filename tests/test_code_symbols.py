"""Tests for Tree-sitter based symbol extraction and search."""

from __future__ import annotations

from pathlib import Path

import pytest

from infrastructure.code_analysis.tree_sitter_parser import parser, SymbolKind
from infrastructure.code_analysis.symbol_search import SymbolSearchService


@pytest.mark.asyncio
async def test_python_symbol_extraction(tmp_path: Path) -> None:
    file_path = tmp_path / "module.py"
    file_path.write_text(
        """class Foo:\n    def method(self):\n        return 1\n\n\ndef func():\n    return 2\n""",
        encoding="utf-8",
    )

    symbols = await parser.parse_file(str(file_path))
    names_kinds = {(s.name, s.kind) for s in symbols}

    assert ("Foo", SymbolKind.CLASS) in names_kinds
    assert ("method", SymbolKind.METHOD) in names_kinds
    assert ("func", SymbolKind.FUNCTION) in names_kinds

    foo = next(s for s in symbols if s.name == "Foo")
    assert foo.body is not None and "class Foo" in foo.body


@pytest.mark.asyncio
async def test_typescript_symbol_extraction(tmp_path: Path) -> None:
    file_path = tmp_path / "module.ts"
    file_path.write_text(
        (
            "export class Bar\n{\n  baz(): number { return 1; }\n}" "\n\n"
            "export function qux(): void { }\n"
        ),
        encoding="utf-8",
    )

    symbols = await parser.parse_file(str(file_path))
    names_kinds = {(s.name, s.kind) for s in symbols}

    assert ("Bar", SymbolKind.CLASS) in names_kinds
    assert ("baz", SymbolKind.METHOD) in names_kinds
    assert ("qux", SymbolKind.FUNCTION) in names_kinds


@pytest.mark.asyncio
async def test_symbol_search_by_name(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "a.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")
    (repo_root / "b.py").write_text("def beta():\n    return 2\n", encoding="utf-8")

    service = SymbolSearchService(project_id="proj-test")
    await service.index_repository(str(repo_root))

    results = await service.search("alp", kinds=[SymbolKind.FUNCTION], fuzzy=True)

    assert results
    top = results[0]
    assert top.symbol.name == "alpha"
    assert top.symbol.file_path == "a.py"
