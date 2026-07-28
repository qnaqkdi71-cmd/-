"""AI 글쓰기 제공자 추상화.

LLM_PROVIDER 환경변수로 gemini / vertex / claude / none 을 고른다.
- gemini : AI Studio API 키 (google-genai, api_key)
- vertex : Google Cloud Vertex AI (서비스 계정 인증) — 크레딧 계정에서 'AQ. 키' 문제 없이 사용
- claude : anthropic
- none   : 키 없음 → AI 호출 없이 골격만 생성

핵심: 나머지 코드는 provider를 몰라도 되고, .env만 바꾸면 전환된다.
"""

from __future__ import annotations

import os


class LLMError(RuntimeError):
    pass


class LLM:
    def __init__(self):
        self.provider = (os.getenv("LLM_PROVIDER") or "none").strip().lower()

    @property
    def available(self) -> bool:
        if self.provider == "gemini":
            return bool(os.getenv("GEMINI_API_KEY"))
        if self.provider == "vertex":
            return bool(os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GEMINI_VERTEX_PROJECT"))
        if self.provider == "claude":
            return bool(os.getenv("ANTHROPIC_API_KEY"))
        return False

    @property
    def label(self) -> str:
        if self.provider == "gemini":
            return f"Gemini ({os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')})"
        if self.provider == "vertex":
            return f"Vertex ({os.getenv('GEMINI_MODEL', 'gemini-2.5-pro')})"
        if self.provider == "claude":
            return f"Claude ({os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-5')})"
        return "없음 (골격만)"

    def complete(self, prompt: str) -> str:
        """프롬프트 → 텍스트. 제공자별 분기. 실패 시 LLMError."""
        if self.provider == "gemini":
            return self._gemini(prompt)
        if self.provider == "vertex":
            return self._vertex(prompt)
        if self.provider == "claude":
            return self._claude(prompt)
        raise LLMError("LLM_PROVIDER가 none 입니다 (AI 글쓰기 비활성).")

    # ── Gemini (무료) ──
    def _gemini(self, prompt: str) -> str:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise LLMError("GEMINI_API_KEY 가 없습니다. .env에 넣어주세요.")
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        try:
            from google import genai  # lazy import
        except ImportError as e:
            raise LLMError("google-genai 미설치: pip install google-genai") from e
        try:
            client = genai.Client(api_key=key)
            resp = client.models.generate_content(model=model, contents=prompt)
            return (resp.text or "").strip()
        except Exception as e:
            raise LLMError(f"Gemini 호출 실패: {e}") from e

    # ── Vertex AI (서비스 계정 인증, 크레딧 계정용) ──
    def _vertex(self, prompt: str) -> str:
        project = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GEMINI_VERTEX_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION") or os.getenv("GEMINI_VERTEX_LOCATION", "global")
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
        if not project:
            raise LLMError("GEMINI_VERTEX_PROJECT(프로젝트 ID)가 없습니다.")
        try:
            from google import genai  # lazy import
        except ImportError as e:
            raise LLMError("google-genai 미설치: pip install google-genai") from e
        try:
            client = genai.Client(vertexai=True, project=project, location=location)
            resp = client.models.generate_content(model=model, contents=prompt)
            return (resp.text or "").strip()
        except Exception as e:
            raise LLMError(f"Vertex 호출 실패: {e}") from e

    # ── Claude (나중에) ──
    def _claude(self, prompt: str) -> str:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise LLMError("ANTHROPIC_API_KEY 가 없습니다.")
        model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
        try:
            import anthropic  # lazy import
        except ImportError as e:
            raise LLMError("anthropic 미설치: pip install anthropic") from e
        try:
            client = anthropic.Anthropic(api_key=key)
            msg = client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(
                block.text for block in msg.content if getattr(block, "type", "") == "text"
            ).strip()
        except Exception as e:
            raise LLMError(f"Claude 호출 실패: {e}") from e
