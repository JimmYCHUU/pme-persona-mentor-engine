"""SQLAlchemy model for saved session snapshots."""

from sqlalchemy import Column, Text

from core.database import Base


class SessionSnapshot(Base):
    """Persisted chat/work snapshot used by resume flow."""

    __tablename__ = "sessions"

    session_id = Column(Text, primary_key=True)
    persona_id = Column(Text, nullable=False, index=True)
    created_at = Column(Text, nullable=False)
    updated_at = Column(Text, nullable=False)
    mode = Column(Text, nullable=False)
    snapshot_json = Column(Text, nullable=False)
