import contextlib

from sqlalchemy import Engine, NullPool, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm import sessionmaker

from app.settings import settings


async def get_async_engine() -> AsyncEngine:
    url = settings.DB_DSN.replace('postgresql', 'postgresql+asyncpg')
    session_engine = create_async_engine(url, poolclass=NullPool, future=True)
    return session_engine


def get_engine() -> Engine:
    session_engine = create_engine(settings.DB_DSN, poolclass=NullPool, future=True)
    return session_engine


def get_session(
    session_engine: Engine | AsyncEngine, is_async: bool = False
) -> sessionmaker | async_sessionmaker:

    sessionmaker_func, session_class = (
        (async_sessionmaker, AsyncSessionType) if is_async else (sessionmaker, SessionType)
    )
    session = sessionmaker_func(
        bind=session_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=session_class,
    )
    return session


@contextlib.contextmanager
def get_sync_session(schema: str | None = None) -> SessionType:
    database_schema = schema or settings.DATABASE_SCHEMA

    engine = get_engine()
    session = get_session(session_engine=engine)
    with session() as sync_session:
        try:
            conn = sync_session.connection()
            conn.execution_options(schema_translate_map={None: database_schema})
            yield sync_session
        finally:
            sync_session.close()


@contextlib.asynccontextmanager
async def get_async_session(schema: str | None = None) -> AsyncSessionType:
    """Асинхронный контекстный менеджер подключения к базе данных."""
    database_schema = schema or settings.DATABASE_SCHEMA
    session = get_session(session_engine=await get_async_engine(), is_async=True)
    async with session() as async_session:
        try:
            conn = await async_session.connection()
            await conn.execution_options(schema_translate_map={None: database_schema})
            yield async_session
        finally:
            await async_session.close()


Session = get_sync_session
AsyncSession = get_async_session
