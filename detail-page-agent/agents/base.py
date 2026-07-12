"""에이전트 공통 실행기.

- 실제 모드: Claude를 tool-use로 호출해 Pydantic 스키마에 맞는 구조화
  출력을 강제하고 검증한다.
- mock 모드: ANTHROPIC_API_KEY가 없거나 --mock이면 각 에이전트가 제공한
  샘플 데이터를 반환한다. 키 없이도 파이프라인 전체가 돈다.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Type, TypeVar

from pydantic import BaseModel

from config import PROMPTS_DIR, has_api_key

T = TypeVar("T", bound=BaseModel)

_client = None


def _get_client():
    global _client
    if _client is None:
        from anthropic import Anthropic

        _client = Anthropic()
    return _client


def load_prompt(name: str) -> str:
    """prompts/<name>.md 시스템 프롬프트를 읽는다."""
    path = Path(PROMPTS_DIR) / f"{name}.md"
    return path.read_text(encoding="utf-8")


def run_agent(
    *,
    name: str,
    model: str,
    user_content: str,
    schema: Type[T],
    mock_provider: Callable[[], T],
    use_mock: bool = False,
    max_tokens: int = 8000,
) -> T:
    """에이전트 한 단계를 실행하고 검증된 Pydantic 객체를 반환한다.

    Claude에는 스키마 이름의 tool을 하나 주고 tool_choice로 강제해,
    자유 텍스트가 아니라 스키마에 맞는 JSON을 받아온다.
    """
    if use_mock or not has_api_key():
        return mock_provider()

    system = load_prompt(name)
    tool_name = f"emit_{name}"
    tool = {
        "name": tool_name,
        "description": f"{name} 단계의 결과를 구조화된 데이터로 반환한다.",
        "input_schema": schema.model_json_schema(),
    }
    client = _get_client()
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        tools=[tool],
        tool_choice={"type": "tool", "name": tool_name},
        messages=[{"role": "user", "content": user_content}],
    )
    for block in message.content:
        if getattr(block, "type", None) == "tool_use" and block.name == tool_name:
            return schema.model_validate(block.input)
    raise RuntimeError(f"[{name}] Claude가 구조화 출력을 반환하지 않았습니다.")
