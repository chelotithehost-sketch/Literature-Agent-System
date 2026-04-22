# core/llm_interface.py
import asyncio
import aiohttp
import json
from typing import Optional, Dict, List, Any
from loguru import logger
import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class LLMProvider:
    """Unified interface for OpenAI-compatible APIs and Ollama."""
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get("provider", "openai")  # openai, ollama, etc.
        self.model = config["model"]
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        self.timeout = config.get("timeout", 120)
        self.max_retries = config.get("max_retries", 3)
        self.cost_per_1k = config.get("cost_per_1k", 0.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def complete(self, messages: List[Dict[str, str]], **kwargs) -> str:
        if self.provider == "ollama":
            return await self._ollama_complete(messages, **kwargs)
        else:
            return await self._openai_complete(messages, **kwargs)

    async def _openai_complete(self, messages, **kwargs):
        client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=0  # handled by tenacity
        )
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
            top_p=kwargs.get("top_p", 1.0),
            frequency_penalty=kwargs.get("frequency_penalty", 0.0),
            presence_penalty=kwargs.get("presence_penalty", 0.0),
        )
        return response.choices[0].message.content

    async def _ollama_complete(self, messages, **kwargs):
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2048),
                "top_p": kwargs.get("top_p", 1.0),
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=self.timeout) as resp:
                data = await resp.json()
                return data["message"]["content"]
