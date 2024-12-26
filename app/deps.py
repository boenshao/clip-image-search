from collections.abc import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
