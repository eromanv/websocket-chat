from fastapi import FastAPI, WebSocket, Depends, HTTPException, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from alembic import command, config
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

app = FastAPI()


async def get_db():
    """Provides a database session for dependency injection."""
    async with SessionLocal() as session:
        yield session


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


Chat.messages = relationship(
    "Message", order_by=Message.timestamp, back_populates="chat"
)


class MessageCreate(BaseModel):
    chat_id: int
    sender_id: int
    receiver_id: int
    text: str


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    receiver_id: int
    text: str
    timestamp: datetime

    class Config:
        from_attributes = True


active_connections = {}


@app.websocket("/ws/{chat_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, chat_id: int, user_id: int, db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for chat communication."""
    await websocket.accept()
    if chat_id not in active_connections:
        active_connections[chat_id] = []
    active_connections[chat_id].append(websocket)

    result = await db.execute(select(User.id).where(User.id == user_id))
    sender = result.scalars().first()
    if not sender:
        await websocket.send_text("Ошибка: отправитель не найден.")
        await websocket.close()
        return

    result = await db.execute(select(User.id).where(User.id != user_id))
    receiver = result.scalars().first()
    if not receiver:
        await websocket.send_text("Ошибка: второй участник чата не найден.")
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_text()
            message = Message(
                chat_id=chat_id,
                sender_id=user_id,
                receiver_id=receiver,
                text=data,
                timestamp=datetime.utcnow(),
            )
            db.add(message)
            await db.commit()
            await db.refresh(message)

            message_response = MessageResponse.from_orm(message)

            for connection in active_connections[chat_id]:
                await connection.send_json(message_response.model_dump())
    except WebSocketDisconnect:
        active_connections[chat_id].remove(websocket)


@app.get("/history/{chat_id}")
async def get_chat_history(
    chat_id: int, limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    """Fetch chat history with pagination."""
    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.timestamp)
        .offset(offset)
        .limit(limit)
    )
    messages = result.scalars().all()
    return {"messages": messages}
