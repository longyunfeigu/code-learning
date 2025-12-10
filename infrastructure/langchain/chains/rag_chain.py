"""
RAG 检索链 - 代码问答

提供基于检索增强生成的代码问答能力。

主要功能：
- create_rag_chain: 通用 RAG Chain，支持同步和异步
- create_code_qa_chain: 代码问答专用 Chain
- create_streaming_rag_chain: 流式输出 Chain
- create_analysis_chain: 分析文档生成 Chain
"""

from typing import Optional, Any, AsyncIterator, Iterator, Dict, List, Callable, Union
from functools import partial

from core.logging_config import get_logger
from ..llm import get_llm
from ..retrievers import get_code_retriever
from ..prompts.code_explain import CODE_EXPLAIN_SYSTEM, CODE_EXPLAIN_PROMPT

logger = get_logger(__name__)


# ============================================================================
# 文档格式化函数
# ============================================================================

def format_docs(docs: List[Any]) -> str:
    """
    格式化检索结果为 Markdown 格式
    
    Args:
        docs: LangChain Document 列表
    
    Returns:
        str: 格式化的文档字符串
    """
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        start_line = doc.metadata.get("start_line", "?")
        end_line = doc.metadata.get("end_line", "?")
        language = doc.metadata.get("language", "")
        symbol_type = doc.metadata.get("symbol_type", "")
        symbol_name = doc.metadata.get("symbol_name", "")
        
        header = f"## [{i}] {source}"
        if symbol_name:
            header += f" - {symbol_type}: {symbol_name}"
        header += f" (L{start_line}-{end_line})"
        
        formatted.append(
            f"{header}\n"
            f"```{language}\n{doc.page_content}\n```"
        )
    return "\n\n".join(formatted)


def format_docs_with_scores(docs_with_scores: List[tuple]) -> str:
    """
    格式化带分数的检索结果
    
    Args:
        docs_with_scores: (Document, score) 元组列表
    
    Returns:
        str: 格式化的文档字符串，包含相似度分数
    """
    formatted = []
    for i, (doc, score) in enumerate(docs_with_scores, 1):
        source = doc.metadata.get("source", "unknown")
        language = doc.metadata.get("language", "")
        
        formatted.append(
            f"## [{i}] {source} (相似度: {score:.3f})\n"
            f"```{language}\n{doc.page_content}\n```"
        )
    return "\n\n".join(formatted)


# ============================================================================
# RAG Chain 创建函数
# ============================================================================

def create_rag_chain(
    retriever: Any,
    llm: Optional[Any] = None,
    system_prompt: str = CODE_EXPLAIN_SYSTEM,
    human_prompt: str = CODE_EXPLAIN_PROMPT,
    doc_formatter: Optional[Callable] = None,
):
    """
    创建通用 RAG Chain
    
    Args:
        retriever: LangChain Retriever 实例
        llm: LLM 实例，不指定则使用默认
        system_prompt: 系统提示
        human_prompt: 用户提示模版
        doc_formatter: 自定义文档格式化函数
    
    Returns:
        Runnable: LangChain LCEL Chain
    
    Example:
        >>> retriever = get_code_retriever("proj_123")
        >>> chain = create_rag_chain(retriever)
        >>> response = await chain.ainvoke("解释这段代码")
    """
    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser
    except ImportError:
        raise ImportError(
            "langchain-core is required. Install with: pip install langchain-core"
        )
    
    llm = llm or get_llm()
    formatter = doc_formatter or format_docs
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt),
    ])
    
    # LCEL Chain
    chain = (
        {"context": retriever | formatter, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    logger.debug("created_rag_chain", has_custom_formatter=doc_formatter is not None)
    
    return chain


def create_rag_chain_with_sources(
    retriever: Any,
    llm: Optional[Any] = None,
    system_prompt: str = CODE_EXPLAIN_SYSTEM,
    human_prompt: str = CODE_EXPLAIN_PROMPT,
):
    """
    创建带来源引用的 RAG Chain
    
    返回的结果包含回答和引用的源文档。
    
    Args:
        retriever: LangChain Retriever 实例
        llm: LLM 实例
        system_prompt: 系统提示
        human_prompt: 用户提示模版
    
    Returns:
        Runnable: 返回 {"answer": str, "sources": List[Document]} 的 Chain
    """
    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.runnables import RunnablePassthrough, RunnableParallel
        from langchain_core.output_parsers import StrOutputParser
    except ImportError:
        raise ImportError(
            "langchain-core is required. Install with: pip install langchain-core"
        )
    
    llm = llm or get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt),
    ])
    
    def pass_docs(docs):
        """保留原始文档用于引用"""
        return docs
    
    # Chain 返回回答和源文档
    rag_chain = (
        RunnablePassthrough.assign(
            context=lambda x: retriever.invoke(x["question"])
        )
        | RunnablePassthrough.assign(
            answer=lambda x: (
                prompt.invoke({
                    "context": format_docs(x["context"]),
                    "question": x["question"]
                })
                | llm
                | StrOutputParser()
            ).invoke({})
        )
        | (lambda x: {"answer": x["answer"], "sources": x["context"]})
    )
    
    logger.debug("created_rag_chain_with_sources")
    
    return rag_chain


def create_code_qa_chain(
    project_id: str,
    search_k: int = 10,
    llm: Optional[Any] = None,
):
    """
    创建代码问答 RAG Chain
    
    Args:
        project_id: 项目 ID
        search_k: 检索文档数量
        llm: LLM 实例
    
    Returns:
        Runnable: 代码问答 Chain
    
    Example:
        >>> chain = create_code_qa_chain("proj_123")
        >>> response = await chain.ainvoke("这个项目的入口在哪里？")
    """
    retriever = get_code_retriever(project_id, search_k=search_k)
    
    logger.debug(
        "created_code_qa_chain",
        project_id=project_id,
        search_k=search_k,
    )
    
    return create_rag_chain(retriever=retriever, llm=llm)


# ============================================================================
# 流式输出支持
# ============================================================================

async def stream_rag_response(
    chain: Any,
    question: str,
) -> AsyncIterator[str]:
    """
    流式输出 RAG 响应
    
    Args:
        chain: RAG Chain 实例
        question: 用户问题
    
    Yields:
        str: 响应片段
    
    Example:
        >>> chain = create_code_qa_chain("proj_123")
        >>> async for chunk in stream_rag_response(chain, "解释入口函数"):
        ...     print(chunk, end="", flush=True)
    """
    logger.debug("streaming_rag_response", question_length=len(question))
    
    async for chunk in chain.astream(question):
        yield chunk


def stream_rag_response_sync(
    chain: Any,
    question: str,
) -> Iterator[str]:
    """
    同步流式输出 RAG 响应
    
    Args:
        chain: RAG Chain 实例
        question: 用户问题
    
    Yields:
        str: 响应片段
    """
    logger.debug("streaming_rag_response_sync", question_length=len(question))
    
    for chunk in chain.stream(question):
        yield chunk


async def answer_code_question(
    project_id: str,
    question: str,
    search_k: int = 10,
    streaming: bool = False,
) -> Union[str, AsyncIterator[str]]:
    """
    回答代码相关问题的便捷函数
    
    Args:
        project_id: 项目 ID
        question: 用户问题
        search_k: 检索文档数量
        streaming: 是否流式返回
    
    Returns:
        str | AsyncIterator[str]: AI 回答，流式模式返回异步迭代器
    
    Example:
        # 非流式
        >>> answer = await answer_code_question("proj_123", "入口在哪里？")
        
        # 流式
        >>> async for chunk in await answer_code_question("proj_123", "入口在哪里？", streaming=True):
        ...     print(chunk, end="")
    """
    chain = create_code_qa_chain(project_id, search_k=search_k)
    
    if streaming:
        return stream_rag_response(chain, question)
    
    response = await chain.ainvoke(question)
    return response


async def answer_code_question_with_sources(
    project_id: str,
    question: str,
    search_k: int = 10,
) -> Dict[str, Any]:
    """
    回答代码问题并返回引用来源
    
    Args:
        project_id: 项目 ID
        question: 用户问题
        search_k: 检索文档数量
    
    Returns:
        dict: {"answer": str, "sources": List[Document]}
    """
    retriever = get_code_retriever(project_id, search_k=search_k)
    chain = create_rag_chain_with_sources(retriever)
    
    result = await chain.ainvoke({"question": question})
    
    logger.debug(
        "answered_with_sources",
        project_id=project_id,
        source_count=len(result.get("sources", [])),
    )
    
    return result


# ============================================================================
# 分析文档生成 Chain
# ============================================================================

def create_analysis_chain(
    retriever: Any,
    analysis_type: str = "architecture",
    llm: Optional[Any] = None,
):
    """
    创建分析文档生成 Chain
    
    Args:
        retriever: 代码检索器
        analysis_type: 分析类型 (architecture, module, class, method, flow)
        llm: LLM 实例
    
    Returns:
        Runnable: 分析 Chain
    """
    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser
    except ImportError:
        raise ImportError(
            "langchain-core is required. Install with: pip install langchain-core"
        )
    
    from ..prompts.analysis import (
        ARCHITECTURE_ANALYSIS_SYSTEM,
        ARCHITECTURE_ANALYSIS_PROMPT,
        MODULE_ANALYSIS_PROMPT,
        CORE_CLASS_ANALYSIS_PROMPT,
        KEY_METHOD_ANALYSIS_PROMPT,
        CORE_FLOW_ANALYSIS_PROMPT,
    )
    
    # 根据分析类型选择 Prompt
    prompt_map = {
        "architecture": ARCHITECTURE_ANALYSIS_PROMPT,
        "module": MODULE_ANALYSIS_PROMPT,
        "class": CORE_CLASS_ANALYSIS_PROMPT,
        "method": KEY_METHOD_ANALYSIS_PROMPT,
        "flow": CORE_FLOW_ANALYSIS_PROMPT,
    }
    
    human_prompt = prompt_map.get(analysis_type, ARCHITECTURE_ANALYSIS_PROMPT)
    
    llm = llm or get_llm(temperature=0.3)  # 分析任务使用较低温度
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", ARCHITECTURE_ANALYSIS_SYSTEM),
        ("human", human_prompt),
    ])
    
    # 分析 Chain - 接受结构化输入
    chain = prompt | llm | StrOutputParser()
    
    logger.debug("created_analysis_chain", analysis_type=analysis_type)
    
    return chain


async def generate_project_analysis(
    project_id: str,
    analysis_type: str = "architecture",
    project_info: Optional[Dict[str, Any]] = None,
    search_k: int = 20,
) -> str:
    """
    生成项目分析文档
    
    Args:
        project_id: 项目 ID
        analysis_type: 分析类型
        project_info: 项目信息字典
        search_k: 检索代码片段数量
    
    Returns:
        str: Markdown 格式的分析文档
    """
    # 获取代码上下文
    retriever = get_code_retriever(project_id, search_k=search_k)
    
    # 检索相关代码
    docs = await retriever.ainvoke(f"{project_info.get('project_name', '')} 架构 入口 核心")
    code_context = format_docs(docs)
    
    # 准备输入
    chain_input = {
        "project_name": project_info.get("project_name", "Unknown"),
        "project_type": project_info.get("project_type", "Unknown"),
        "language": project_info.get("language", "Unknown"),
        "description": project_info.get("description", ""),
        "project_structure": project_info.get("structure", ""),
        "code_context": code_context,
    }
    
    # 创建并运行 Chain
    chain = create_analysis_chain(retriever, analysis_type=analysis_type)
    result = await chain.ainvoke(chain_input)
    
    logger.info(
        "generated_analysis",
        project_id=project_id,
        analysis_type=analysis_type,
        output_length=len(result),
    )
    
    return result


# ============================================================================
# 多轮对话支持
# ============================================================================

def create_conversational_rag_chain(
    retriever: Any,
    llm: Optional[Any] = None,
    system_prompt: str = CODE_EXPLAIN_SYSTEM,
):
    """
    创建支持多轮对话的 RAG Chain
    
    Args:
        retriever: 代码检索器
        llm: LLM 实例
        system_prompt: 系统提示
    
    Returns:
        Runnable: 对话 Chain，接受 {"question": str, "chat_history": List} 输入
    
    Example:
        >>> chain = create_conversational_rag_chain(retriever)
        >>> result = await chain.ainvoke({
        ...     "question": "这个函数做什么？",
        ...     "chat_history": [
        ...         ("解释一下项目结构", "这个项目使用了分层架构..."),
        ...     ]
        ... })
    """
    try:
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.messages import HumanMessage, AIMessage
    except ImportError:
        raise ImportError(
            "langchain-core is required. Install with: pip install langchain-core"
        )
    
    llm = llm or get_llm()
    
    # 带历史的 Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", """基于以下代码上下文回答问题：

代码上下文：
{context}

问题：{question}"""),
    ])
    
    def format_chat_history(history: List[tuple]) -> List:
        """格式化对话历史"""
        messages = []
        for human, ai in history:
            messages.append(HumanMessage(content=human))
            messages.append(AIMessage(content=ai))
        return messages
    
    # Chain
    chain = (
        RunnablePassthrough.assign(
            context=lambda x: format_docs(retriever.invoke(x["question"])),
            chat_history=lambda x: format_chat_history(x.get("chat_history", [])),
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    logger.debug("created_conversational_rag_chain")
    
    return chain

