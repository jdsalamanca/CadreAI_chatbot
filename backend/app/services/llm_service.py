import httpx

from app.config import settings


class LLMTimeoutError(Exception):
    pass


class LLMUnavailableError(Exception):
    pass


class LLMService:
    """Thin client around OpenRouter's chat completions and responses endpoints."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.openrouter_base_url,
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            timeout=settings.llm_timeout_seconds,
        )

    async def generate_reply(self, messages: list[dict]) -> str:
        try:
            response = await self._client.post(
                "/chat/completions",
                json={"model": settings.openrouter_model, "messages": messages},
            )
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError("The AI service timed out.") from exc
        except httpx.HTTPError as exc:
            raise LLMUnavailableError("The AI service is unreachable.") from exc

        if response.status_code >= 400:
            raise LLMUnavailableError(
                f"The AI service returned an error (status {response.status_code})."
            )

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise LLMUnavailableError("The AI service returned an empty response.")

        content = choices[0].get("message", {}).get("content")
        if not content:
            raise LLMUnavailableError("The AI service returned an empty response.")

        return content

    async def generate_reply_with_web_search(self, messages: list[dict]) -> str:
        try:
            response = await self._client.post(
                "/responses",
                json={
                    "model": settings.openrouter_model,
                    "input": self._to_responses_input(messages),
                    "plugins": [{"id": "web", "max_results": 3}],
                    "max_output_tokens": 9000,
                },
            )
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError("The AI service timed out.") from exc
        except httpx.HTTPError as exc:
            raise LLMUnavailableError("The AI service is unreachable.") from exc

        if response.status_code >= 400:
            raise LLMUnavailableError(
                f"The AI service returned an error (status {response.status_code})."
            )

        data = response.json()
        content = self._extract_response_text(data)
        if not content:
            raise LLMUnavailableError("The AI service returned an empty response.")

        return content

    @staticmethod
    def _to_responses_input(messages: list[dict]) -> list[dict]:
        structured_messages: list[dict] = []
        for message in messages:
            role = message.get("role")
            content = message.get("content", "")
            if role not in {"system", "user", "assistant"}:
                continue
            if not isinstance(content, str) or not content.strip():
                continue

            structured_messages.append(
                {
                    "type": "message",
                    "role": role,
                    "content": [{"type": "input_text", "text": content}],
                }
            )

        return structured_messages

    @staticmethod
    def _extract_response_text(data: dict) -> str:
        output_text = data.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        parts: list[str] = []
        for item in data.get("output", []) or []:
            if not isinstance(item, dict) or item.get("type") != "message":
                continue

            for content in item.get("content", []) or []:
                if not isinstance(content, dict):
                    continue
                if content.get("type") in {"output_text", "text"}:
                    text = content.get("text")
                    if isinstance(text, str) and text.strip():
                        parts.append(text)

        return "".join(parts).strip()
