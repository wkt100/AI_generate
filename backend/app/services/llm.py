import re
import json
import httpx
import logging
from typing import Optional
from app.config import Config

logger = logging.getLogger(__name__)


def extract_json(text: str) -> str:
    """
    从 LLM 输出中提取纯 JSON。
    处理常见的 Markdown 包裹情况: ```json ... ``` 或 ``` ... ```
    """
    # 移除 Markdown code blocks
    patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
        r'(\{[\s\S]*\})',  # 直接找第一个 {...}
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            potential = match.group(1) if '```' in pattern else match.group(0)
            try:
                json.loads(potential.strip())
                return potential.strip()
            except json.JSONDecodeError:
                continue

    # 最后尝试直接解析原文本
    return text.strip()


async def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    response_format: Optional[dict] = None
) -> str:
    """
    调用 LLM API (Minimax)。
    返回纯文本响应。
    """
    if Config.LLM_PROVIDER == "minimax":
        return await _call_minimax(prompt, system_prompt, response_format)
    else:
        raise ValueError(f"Unsupported LLM provider: {Config.LLM_PROVIDER}")


async def _call_minimax(
    prompt: str,
    system_prompt: Optional[str] = None,
    response_format: Optional[dict] = None
) -> str:
    """调用 Minimax API"""
    url = f"{Config.MINIMAX_BASE_URL}/text/chatcompletion_v2"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "MiniMax-M2.7",
        "messages": messages,
    }

    if response_format:
        payload["response_format"] = response_format

    headers = {
        "Authorization": f"Bearer {Config.MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=Config.AGENT_TIMEOUT) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        # 处理不同响应格式
        choices = data.get("choices")
        if choices and len(choices) > 0:
            return choices[0]["message"]["content"]

        # 检查错误信息
        base_resp = data.get("base_resp", {})
        if base_resp.get("status_code") != 0:
            error_msg = base_resp.get("status_msg", "Unknown error")
            raise ValueError(f"Minimax API error: {error_msg}")

        raise ValueError(f"Unexpected API response: {data}")


async def call_llm_json(prompt: str, system_prompt: Optional[str] = None) -> dict:
    """
    调用 LLM 并强制返回 JSON。
    自动处理 Markdown 包裹和解析错误。
    """
    raw_text = await call_llm(
        prompt,
        system_prompt,
        response_format={"type": "json_object"}
    )

    clean_text = extract_json(raw_text)

    try:
        return json.loads(clean_text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nRaw: {raw_text}\nClean: {clean_text}")
        raise ValueError(f"Failed to parse LLM response as JSON: {clean_text[:200]}")
