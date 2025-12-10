"""
LangChain Chain 模块

包含各种预定义的 Chain：
- rag_chain.py: RAG 检索链，支持流式输出和多轮对话

主要导出：
- create_rag_chain: 通用 RAG Chain
- create_code_qa_chain: 代码问答 Chain
- create_rag_chain_with_sources: 带来源引用的 RAG Chain
- create_analysis_chain: 分析文档生成 Chain
- create_conversational_rag_chain: 多轮对话 Chain
- stream_rag_response: 异步流式输出
- answer_code_question: 便捷问答函数
- generate_project_analysis: 生成项目分析文档
"""

from .rag_chain import (
    # Chain 创建函数
    create_rag_chain,
    create_code_qa_chain,
    create_rag_chain_with_sources,
    create_analysis_chain,
    create_conversational_rag_chain,
    # 流式输出
    stream_rag_response,
    stream_rag_response_sync,
    # 便捷函数
    answer_code_question,
    answer_code_question_with_sources,
    generate_project_analysis,
    # 文档格式化
    format_docs,
    format_docs_with_scores,
)

__all__ = [
    # Chain 创建
    "create_rag_chain",
    "create_code_qa_chain",
    "create_rag_chain_with_sources",
    "create_analysis_chain",
    "create_conversational_rag_chain",
    # 流式输出
    "stream_rag_response",
    "stream_rag_response_sync",
    # 便捷函数
    "answer_code_question",
    "answer_code_question_with_sources",
    "generate_project_analysis",
    # 文档格式化
    "format_docs",
    "format_docs_with_scores",
]

