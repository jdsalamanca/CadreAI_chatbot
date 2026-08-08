import httpx

from app.config import settings


class LLMTimeoutError(Exception):
    pass


class LLMUnavailableError(Exception):
    pass


class LLMService:
    """Thin client around OpenRouter's chat completions endpoint."""

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
