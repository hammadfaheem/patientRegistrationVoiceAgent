"""Application configuration, built from environment variables."""

from dataclasses import dataclass

from .env import get_env


@dataclass(frozen=True)
class Config:
    """Runtime configuration for the patient registration agent."""

    api_base_url: str
    api_timeout_seconds: float
    log_level: str


config = Config(
    api_base_url=(get_env("API_BASE_URL") or "http://localhost:8000").rstrip("/"),
    api_timeout_seconds=float(get_env("API_TIMEOUT_SECONDS") or "10"),
    log_level=get_env("LOG_LEVEL") or "INFO",
)
