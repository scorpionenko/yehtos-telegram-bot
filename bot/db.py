import asyncpg

pool = None


async def connect_db():
    global pool
    pool = await asyncpg.create_pool(
        user="postgres",
        password="4791553",
        database="yehtos",
        host="localhost"
    )

def get_pool():
    return pool

async def init_tables():
    query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        user_id BIGINT UNIQUE,
        username TEXT,
        role TEXT DEFAULT 'user',
        is_verified BOOLEAN DEFAULT FALSE,
        certificate_file_id TEXT,
        rating FLOAT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    async with pool.acquire() as conn:
        await conn.execute(query)