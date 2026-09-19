import asyncio

from sqlalchemy import text

from app.db.database import engine


async def test_connection():
    async with engine.connect() as connection:
        result = await connection.execute(
            text("SELECT current_database()")
        )

        print(f"Connected to database: {result.scalar()}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection())