from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from database import Base

class URL(Base):
    __tablename__ = "urls"

    id            = Column(Integer, primary_key=True, index=True)
    short_code    = Column(String(10), unique=True, index=True)
    long_url      = Column(String(2048), nullable=False)
    hit_count     = Column(Integer, default=0)
    created_at    = Column(DateTime, server_default=func.now())
    last_accessed = Column(DateTime, nullable=True)