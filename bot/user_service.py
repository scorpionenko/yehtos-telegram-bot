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

async def set_role(user_id: int, role: str):
    query = "UPDATE users SET role = $1 WHERE user_id = $2"

    pool = get_pool()

    async with pool.acquire() as conn:
        await conn.execute(query, role, user_id)


async def set_verified(user_id: int, value: bool):
    query = "UPDATE users SET is_verified = $1 WHERE user_id = $2"

    pool = get_pool()

    async with pool.acquire() as conn:
        await conn.execute(query, value, user_id) 

from bot.db import get_pool

async def get_user(user_id: int):
    query = "SELECT * FROM users WHERE user_id = $1"

    pool = get_pool()

    async with pool.acquire() as conn:
        return await conn.fetchrow(query, user_id)               