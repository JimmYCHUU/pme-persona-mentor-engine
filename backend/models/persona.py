"""Persona SQLAlchemy model."""

from sqlalchemy import Column, String, Text, DateTime
from core.database import Base
import datetime


class PersonaProfile(Base):
    """Represents a mentor persona profile."""

    __tablename__ = 'persona_profiles'

    persona_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, default='')
    soul_json = Column(Text, default='{}')
    sliders_json = Column(Text, default='{}')
    vault_collections = Column(Text, default='[]')
    fingerprint_collections = Column(Text, default='[]')
    gap_fill_json = Column(Text, default='{}')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
