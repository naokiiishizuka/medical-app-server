"""Database configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _get_bool(env_value: str | None, default: bool = False) -> bool:
    if env_value is None:
        return default
    return env_value.lower() in {"1", "true", "t", "yes", "y"}


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set. Provide it via environment variable or .env file."
        )
    return value


@dataclass(frozen=True)
class DatabaseConfig:
    """Application database settings resolved from environment variables."""

    url: str
    echo: bool


@lru_cache(maxsize=1)
def get_database_config() -> DatabaseConfig:
    """Return the cached database configuration."""

    return DatabaseConfig(
        url=_require_env("DATABASE_URL"),
        echo=_get_bool(os.getenv("DATABASE_ECHO"), default=False),
    )
