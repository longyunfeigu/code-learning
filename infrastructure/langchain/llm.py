"""
LLM 配置模块 - 通过 LangChain 统一封装

支持多种 LLM 提供商：
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Ollama (本地模型)

使用示例:
    >>> from infrastructure.langchain import get_llm
    >>> llm = get_llm()  # 使用默认配置
    >>> llm = get_llm(provider="openai", model="gpt-4-turbo")
    >>> response = await llm.ainvoke("Hello!")
"""

from typing import Optional, Literal, Union
from functools import lru_cache

from langchain_core.language_models import BaseChatModel

from core.config import settings
from core.logging_config import get_logger
from .exceptions import LLMProviderError, LLMConfigError

logger = get_logger(__name__)

# LLM 提供商类型
LLMProvider = Literal["openai", "anthropic", "ollama"]


def get_llm(
    provider: Optional[LLMProvider] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    streaming: bool = False,
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None,
) -> BaseChatModel:
    """
    获取 LLM 实例 - 统一接口，一行代码切换模型
    
    Args:
        provider: 模型提供商 (openai, anthropic, ollama)，默认从配置读取
        model: 模型名称，不指定则使用配置默认值
        temperature: 温度参数 (0.0-2.0)
        max_tokens: 最大生成 token 数
        streaming: 是否启用流式输出
        timeout: 请求超时时间（秒）
        max_retries: 最大重试次数
    
    Returns:
        BaseChatModel: LangChain ChatModel 实例
    
    Raises:
        LLMProviderError: 不支持的 provider
        LLMConfigError: 配置错误（如缺少 API Key）
    
    Example:
        >>> llm = get_llm()  # 使用默认配置
        >>> llm = get_llm(provider="openai", model="gpt-4-turbo")
        >>> llm = get_llm(provider="anthropic", model="claude-3-opus")
        >>> llm = get_llm(streaming=True)  # 启用流式输出
    """
    provider = provider or settings.llm.provider
    model = model or settings.llm.model
    temperature = temperature if temperature is not None else settings.llm.temperature
    timeout = timeout or settings.llm.timeout
    max_retries = max_retries if max_retries is not None else settings.llm.max_retries
    
    logger.debug(
        "creating_llm",
        provider=provider,
        model=model,
        temperature=temperature,
        streaming=streaming,
        timeout=timeout,
    )
    
    if provider == "openai":
        return _get_openai_llm(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            timeout=timeout,
            max_retries=max_retries,
        )
    elif provider == "anthropic":
        return _get_anthropic_llm(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            timeout=timeout,
            max_retries=max_retries,
        )
    elif provider == "ollama":
        return _get_ollama_llm(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
        )
    else:
        raise LLMProviderError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: openai, anthropic, ollama"
        )


def _get_openai_llm(
    model: str,
    temperature: float,
    max_tokens: Optional[int],
    streaming: bool,
    timeout: int,
    max_retries: int,
) -> BaseChatModel:
    """获取 OpenAI ChatModel"""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        raise LLMProviderError(
            "langchain-openai is required for OpenAI provider. "
            "Install with: pip install langchain-openai"
        )
    
    # 验证 API Key
    api_key = settings.openai.api_key
    if not api_key:
        raise LLMConfigError(
            "OpenAI API key is not configured. "
            "Please set OPENAI__API_KEY in environment variables."
        )
    
    kwargs = {
        "model": model,
        "temperature": temperature,
        "api_key": api_key.get_secret_value() if hasattr(api_key, 'get_secret_value') else api_key,
        "streaming": streaming,
        "timeout": timeout,
        "max_retries": max_retries,
    }
    
    if settings.openai.base_url:
        kwargs["base_url"] = settings.openai.base_url
    
    if max_tokens:
        kwargs["max_tokens"] = max_tokens
    
    logger.debug("openai_llm_created", model=model)
    return ChatOpenAI(**kwargs)


def _get_anthropic_llm(
    model: str,
    temperature: float,
    max_tokens: Optional[int],
    streaming: bool,
    timeout: int,
    max_retries: int,
) -> BaseChatModel:
    """获取 Anthropic ChatModel"""
    try:
        from langchain_anthropic import ChatAnthropic
    except ImportError:
        raise LLMProviderError(
            "langchain-anthropic is required for Anthropic provider. "
            "Install with: pip install langchain-anthropic"
        )
    
    # 验证 API Key
    api_key = settings.anthropic.api_key
    if not api_key:
        raise LLMConfigError(
            "Anthropic API key is not configured. "
            "Please set ANTHROPIC__API_KEY in environment variables."
        )
    
    kwargs = {
        "model": model,
        "temperature": temperature,
        "api_key": api_key.get_secret_value() if hasattr(api_key, 'get_secret_value') else api_key,
        "streaming": streaming,
        "timeout": timeout,
        "max_retries": max_retries,
    }
    
    if max_tokens:
        kwargs["max_tokens"] = max_tokens
    
    logger.debug("anthropic_llm_created", model=model)
    return ChatAnthropic(**kwargs)


def _get_ollama_llm(
    model: str,
    temperature: float,
    max_tokens: Optional[int],
    streaming: bool,
) -> BaseChatModel:
    """获取 Ollama ChatModel (本地模型)"""
    try:
        from langchain_ollama import ChatOllama
    except ImportError:
        raise LLMProviderError(
            "langchain-ollama is required for Ollama provider. "
            "Install with: pip install langchain-ollama"
        )
    
    kwargs = {
        "model": model,
        "temperature": temperature,
        "base_url": settings.ollama.base_url,
    }
    
    if max_tokens:
        kwargs["num_predict"] = max_tokens
    
    logger.debug("ollama_llm_created", model=model, base_url=settings.ollama.base_url)
    return ChatOllama(**kwargs)


# =============================================================================
# 缓存 LLM 实例
# =============================================================================

_llm_cache: dict[str, BaseChatModel] = {}


def get_cached_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> BaseChatModel:
    """
    获取缓存的 LLM 实例
    
    用于频繁调用场景，避免重复创建实例。
    注意：不支持 streaming 模式，因为同一实例无法同时用于流式和非流式。
    
    Args:
        provider: 模型提供商
        model: 模型名称
        temperature: 温度参数
    
    Returns:
        BaseChatModel: 缓存的 LLM 实例
    """
    provider = provider or settings.llm.provider
    model = model or settings.llm.model
    temperature = temperature if temperature is not None else settings.llm.temperature
    
    cache_key = f"{provider}:{model}:{temperature}"
    
    if cache_key not in _llm_cache:
        _llm_cache[cache_key] = get_llm(
            provider=provider,
            model=model,
            temperature=temperature,
            streaming=False,
        )
        logger.debug("llm_cached", cache_key=cache_key)
    
    return _llm_cache[cache_key]


def clear_llm_cache():
    """清除 LLM 缓存"""
    _llm_cache.clear()
    logger.debug("llm_cache_cleared")
