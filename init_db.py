from dotenv import load_dotenv
import os
from sqlalchemy.ext.asyncio import AsyncSession
from main import User, Chat, SessionLocal

load_dotenv()


async def init_db():
    """Initialize the database with sample data."""
    async with SessionLocal() as session:
        async with session.begin():
            user1 = User(name="User1")
            user2 = User(name="User2")
            chat = Chat()
            session.add_all([user1, user2, chat])
            await session.commit()


import asyncio

asyncio.run(init_db())
