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

    def diagnose(self) -> dict:
        """실제로 짧은 호출을 한 번 시도해 성공/실패와 정확한 원인을 돌려준다.

        결과 화면(/diag)에서 '왜 골격만 나오는지'를 사용자 화면에 그대로 보여주기 위함.
        """
        import traceback

        info: dict = {
            "provider": self.provider,
            "label": self.label,
            "available": self.available,
            "env": {
                "GEMINI_MODEL": os.getenv("GEMINI_MODEL"),
                "GEMINI_VERTEX_PROJECT": os.getenv("GEMINI_VERTEX_PROJECT")
                or os.getenv("GOOGLE_CLOUD_PROJECT"),
                "GEMINI_VERTEX_LOCATION": os.getenv("GEMINI_VERTEX_LOCATION")
                or os.getenv("GOOGLE_CLOUD_LOCATION"),
                "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
                "GEMINI_API_KEY_set": bool(os.getenv("GEMINI_API_KEY")),
            },
        }

        # 서비스 계정 파일 존재 여부(Vertex)
        cred = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if cred:
            info["cred_exists"] = os.path.isfile(cred)
            info["cred_path"] = cred

        if not self.available:
            info["ok"] = False
            info["error"] = (
                f"제공자 '{self.provider}' 준비 안 됨 — 필수 값이 비어 있습니다. "
                "(vertex면 GEMINI_VERTEX_PROJECT, gemini면 GEMINI_API_KEY 확인)"
            )
            return info

        try:
            out = self.complete("한국어로 딱 한 단어만 답해: 준비완료")
            info["ok"] = True
            info["sample"] = (out or "")[:200]
        except Exception as e:  # noqa: BLE001 — 진단은 모든 오류를 표면화
            info["ok"] = False
            info["error"] = str(e)
            info["traceback"] = traceback.format_exc()[-2000:]
        return info

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

        # 한 모델/리전 조합이 막혀도 골격으로 조용히 떨어지지 않도록 후보를 순서대로 시도.
        # (설정값을 1순위로, 흔히 되는 조합을 폴백으로.)
        model_candidates = [model]
        for m in ("gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"):
            if m not in model_candidates:
                model_candidates.append(m)
        loc_candidates = [location]
        for loc in ("global", "us-central1"):
            if loc not in loc_candidates:
                loc_candidates.append(loc)

        errors: list[str] = []
        for loc in loc_candidates:
            try:
                client = genai.Client(vertexai=True, project=project, location=loc)
            except Exception as e:  # noqa: BLE001
                errors.append(f"[{loc}] 클라이언트 생성 실패: {e}")
                continue
            for mdl in model_candidates:
                try:
                    resp = client.models.generate_content(model=mdl, contents=prompt)
                    text = (resp.text or "").strip()
                    if text:
                        return text
                    errors.append(f"[{loc}/{mdl}] 빈 응답")
                except Exception as e:  # noqa: BLE001
                    msg = str(e)
                    errors.append(f"[{loc}/{mdl}] {msg}")
                    # 인증/권한/사용설정 문제면 다른 조합도 동일하므로 즉시 중단.
                    low = msg.lower()
                    if any(k in low for k in ("permission", "denied", "credential",
                                              "unauthenticated", "not enabled", "disabled",
                                              "403", "401")):
                        raise LLMError("Vertex 호출 실패: " + " | ".join(errors))
        raise LLMError("Vertex 호출 실패: " + " | ".join(errors))

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
