"""Session snapshot SQLAlchemy model."""

from sqlalchemy import Column, String, Text, DateTime
from core.database import Base
import datetime


class Session(Base):
    """Represents a session snapshot."""

    __tablename__ = 'sessions'

    session_id = Column(String, primary_key=True)
    persona_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
    mode = Column(String, default='deep_dive')
    snapshot_json = Column(Text, default='{}')
