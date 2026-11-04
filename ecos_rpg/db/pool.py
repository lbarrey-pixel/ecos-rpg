import asyncpg


async def criar_pool(dsn: str, **kwargs) -> asyncpg.Pool:
    return await asyncpg.create_pool(dsn, min_size=1, max_size=5, **kwargs)
