"""Database engine and session management."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                     async_sessionmaker, create_async_engine)

from src.shared.main.config import get_database_config

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Instantiate (or retrieve) the global async SQLAlchemy engine."""
    global _engine, _session_factory
    if _engine is None:
        cfg = get_database_config()
        _engine = create_async_engine(cfg.url, echo=cfg.echo, pool_pre_ping=True)
        _session_factory = async_sessionmaker(
            _engine, expire_on_commit=False, autoflush=False
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Ensure the session factory exists and return it."""
    global _session_factory
    if _session_factory is None:
        get_engine()
    assert _session_factory is not None  # for mypy
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a database session."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        await session.close()


async def dispose_engine() -> None:
    """Dispose of the engine when shutting down the application."""
    global _engine, _session_factory
    if _session_factory is not None:
        await _session_factory.close_all()
        _session_factory = None
    if _engine is not None:
        await _engine.dispose()
        _engine = None
