"""
This module contains the database session configuration for FastAPI routes.
"""

from config import settings
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

# Ensure the DATABASE_URL uses asyncpg
engine = create_async_engine(settings.db_url)

# Create the session factory for async sessions
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


# Dependency for FastAPI routes
async def get_db():
    """
    Dependency for FastAPI routes.
    :return: Database session.
    """
    async with AsyncSessionLocal() as session:
        yield session
