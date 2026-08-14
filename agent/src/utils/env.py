"""Environment variable loading and access."""

import os

from dotenv import load_dotenv

load_dotenv(".env.local")


def get_env(name: str, default: str | None = None) -> str | None:
    """Read an environment variable, falling back to ``default`` if unset."""
    return os.environ.get(name, default)


def require_env(name: str) -> str:
    """Read a required environment variable, raising if it's missing."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value
