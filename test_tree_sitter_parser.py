"""
测试 tree_sitter_parser.py 的解析功能

用法:
    python test_tree_sitter_parser.py
"""

import asyncio
from pathlib import Path
from infrastructure.code_analysis.tree_sitter_parser import parser, SymbolKind


async def main():
    """主测试函数"""
    # 要解析的文件路径
    file_path = "/Users/guwanhua/git/code-learning/infrastructure/code_analysis/symbol_search.py"

    print("=" * 80)
    print(f"正在解析文件: {file_path}")
    print("=" * 80)
    print()

    # 检查文件是否存在
    if not Path(file_path).exists():
        print(f"❌ 错误: 文件不存在 - {file_path}")
        return

    # 解析文件
    try:
        symbols = await parser.parse_file(file_path)

        if not symbols:
            print("⚠️  未提取到任何符号")
            return

        # 统计信息
        print(f"✅ 成功提取 {len(symbols)} 个符号\n")

        # 按类型统计
        kind_counts = {}
        for symbol in symbols:
            kind_name = symbol.kind.value
            kind_counts[kind_name] = kind_counts.get(kind_name, 0) + 1

        print("📊 符号类型统计:")
        for kind, count in sorted(kind_counts.items()):
            print(f"  - {kind}: {count}")
        print()

        # 详细展示每个符号
        print("📋 符号详情:")
        print("-" * 80)

        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}] {symbol.name}")
            print(f"    类型: {symbol.kind.value}")
            print(f"    位置: {symbol.start_line}:{symbol.start_col} - {symbol.end_line}:{symbol.end_col}")

            if symbol.parent:
                print(f"    父类/父函数: {symbol.parent}")

            if symbol.signature:
                print(f"    签名: {symbol.signature}")

            if symbol.docstring:
                docstring_preview = symbol.docstring[:100]
                if len(symbol.docstring) > 100:
                    docstring_preview += "..."
                print(f"    文档: {docstring_preview}")

            # 显示前几行代码
            if symbol.body:
                lines = symbol.body.split('\n')
                preview_lines = lines[:3]
                print(f"    代码预览:")
                for line in preview_lines:
                    print(f"      {line}")
                if len(lines) > 3:
                    print(f"      ... (共 {len(lines)} 行)")

            # 显示子符号
            if symbol.children:
                print(f"    子符号数量: {len(symbol.children)}")
                for child in symbol.children[:3]:
                    print(f"      - {child.name} ({child.kind.value})")
                if len(symbol.children) > 3:
                    print(f"      ... 还有 {len(symbol.children) - 3} 个")

        print("\n" + "=" * 80)
        print("✅ 测试完成")
        print("=" * 80)

        # 额外测试：验证特定符号
        print("\n🔍 验证特定符号:")

        # 查找 SymbolSearchService 类
        search_service_class = next(
            (s for s in symbols if s.name == "SymbolSearchService" and s.kind == SymbolKind.CLASS),
            None
        )

        if search_service_class:
            print(f"✅ 找到类 'SymbolSearchService'")
            print(f"   位置: {search_service_class.start_line}-{search_service_class.end_line}")
            print(f"   包含方法数: {len(search_service_class.children)}")

            # 列出所有方法
            methods = [s for s in symbols if s.parent == "SymbolSearchService" and s.kind == SymbolKind.METHOD]
            print(f"   方法列表:")
            for method in methods:
                print(f"     - {method.name}()")
        else:
            print("❌ 未找到类 'SymbolSearchService'")

        # 查找 SearchResult 数据类
        search_result_class = next(
            (s for s in symbols if s.name == "SearchResult" and s.kind == SymbolKind.CLASS),
            None
        )

        if search_result_class:
            print(f"\n✅ 找到类 'SearchResult'")
            print(f"   位置: {search_result_class.start_line}-{search_result_class.end_line}")
        else:
            print("\n❌ 未找到类 'SearchResult'")

    except Exception as e:
        print(f"❌ 解析失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
