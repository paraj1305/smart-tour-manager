from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.mutable import MutableDict
from app.database.base import Base
from datetime import datetime

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)
    phone = Column(String(20), index=True, nullable=False)
    state = Column(String(50), default="greeting")  
    data = Column(MutableDict.as_mutable(JSON), default=dict)                
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
