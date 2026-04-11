from bot.db import get_pool

async def create_user(user_id: int, username: str):
    query = """
    INSERT INTO users (user_id, username)
    VALUES ($1, $2)
    ON CONFLICT (user_id) DO NOTHING
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        await conn.execute(query, user_id, username)