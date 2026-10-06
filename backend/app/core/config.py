import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


@dataclass(frozen=True)
class Settings:
    llm_api_key: str | None
    llm_base_url: str
    llm_model: str
    llm_timeout: float


def get_settings() -> Settings:
    return Settings(
        llm_api_key=os.getenv("LLM_API_KEY"),
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
        llm_model=os.getenv("LLM_MODEL", "openai/gpt-oss-20b"),
        llm_timeout=float(os.getenv("LLM_TIMEOUT", "20")),
    )
