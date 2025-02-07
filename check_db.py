from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from main import User, Chat, Message
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def check_db():
    """Check the contents of the database tables."""
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User))
            users = result.scalars().all()
            print("Users in the database:", users)

            result = await session.execute(select(Chat))
            chats = result.scalars().all()
            print("Chats in the database:", chats)

            result = await session.execute(select(Message))
            messages = result.scalars().all()
            print("Messages in the database:", messages)


import asyncio

asyncio.run(check_db())
