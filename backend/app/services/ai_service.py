import json
import logging
from typing import Any

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    RateLimitError,
)

from app.core.config import get_settings
from app.core.exceptions import AIServiceError

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 2  # one retry for transient failures

SYSTEM_PROMPT = (
    "You are an AI Content Assistant. "
    "Analyze the user's text and generate a concise, accurate summary "
    "and exactly three relevant tags. "
    "Return ONLY valid JSON. Do not include markdown, code fences, explanations, "
    "or any additional fields. "
    "The response MUST follow this exact structure: "
    '{"summary":"concise summary","tags":["tag-1","tag-2","tag-3"]}. '
    "The summary must be 2-3 sentences (about 40-70 words) covering the key facts, "
    "problems, decisions and next steps, not just the general theme. "
    "Use only information found in the text. "
    "Each tag should be short, meaningful, and directly related to the content. "
    "Always return exactly three unique tags."
)


def _parse_result(raw: str) -> dict[str, Any]:
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AIServiceError("The AI returned invalid JSON") from exc

    summary = result.get("summary") if isinstance(result, dict) else None
    tags = result.get("tags") if isinstance(result, dict) else None
    if not isinstance(summary, str) or not summary.strip():
        raise AIServiceError("The AI response did not include a valid summary")
    if not isinstance(tags, list) or len(tags) != 3 or any(
        not isinstance(tag, str) or not tag.strip() for tag in tags
    ):
        raise AIServiceError("The AI response must contain exactly three tags")
    return {"summary": summary.strip(), "tags": [tag.strip() for tag in tags]}


def _to_service_error(exc: Exception) -> tuple[AIServiceError, bool]:
    """Map a provider/SDK error to a user-facing error and whether a retry may help."""
    if isinstance(exc, APITimeoutError):
        return AIServiceError("The AI request timed out. Please try again."), True
    if isinstance(exc, APIConnectionError):
        return AIServiceError("Could not reach the AI provider. Please try again."), True
    if isinstance(exc, RateLimitError):
        return AIServiceError("The AI provider is rate limiting requests. Please retry shortly."), True
    if isinstance(exc, AuthenticationError):
        return AIServiceError("The AI provider rejected the API key"), False
    if isinstance(exc, APIStatusError):
        # e.g. 400 json_validate_failed when the model produced invalid JSON, or 5xx
        return AIServiceError("The AI service is temporarily unavailable"), exc.status_code >= 500 or exc.status_code == 400
    return AIServiceError("The AI service is temporarily unavailable"), False


async def generate_content(text: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.llm_api_key:
        raise AIServiceError("LLM_API_KEY is not configured")

    client = AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=settings.llm_timeout,
    )
    try:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = await client.chat.completions.create(
                    model=settings.llm_model,
                    temperature=0.2,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": text},
                    ],
                )
                return _parse_result(response.choices[0].message.content or "")
            except AIServiceError as exc:
                logger.warning("AI output rejected (attempt %d/%d): %s", attempt, MAX_ATTEMPTS, exc)
                error, retryable = exc, True
            except Exception as exc:
                logger.exception("LLM call failed (attempt %d/%d)", attempt, MAX_ATTEMPTS)
                error, retryable = _to_service_error(exc)
            if not retryable or attempt == MAX_ATTEMPTS:
                raise error
    finally:
        await client.close()
