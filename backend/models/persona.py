"""SQLAlchemy model for mentor persona profiles."""

from sqlalchemy import Column, Text

from core.database import Base


class Persona(Base):
    """Persisted persona profile with style and metadata payloads."""

    __tablename__ = "personas"

    persona_id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    soul_json = Column(Text, nullable=False, default="{}")
    sliders_json = Column(Text, nullable=False, default="{}")
    vault_collections = Column(Text, nullable=False, default="[]")
    fingerprint_collections = Column(Text, nullable=False, default="[]")
    gap_fill_json = Column(Text, nullable=False, default="{}")
    created_at = Column(Text, nullable=False)
