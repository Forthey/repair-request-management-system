from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import settings


async_engine = create_async_engine(
    url=settings.get_psycopg_url,
    echo=False,
    pool_size=5,
    max_overflow=10
)

async_session_factory = async_sessionmaker(async_engine)


def get_async_session() -> AsyncSession:
    return async_session_factory()
