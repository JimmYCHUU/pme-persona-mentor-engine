"""Mastery tracking SQLAlchemy models."""

from sqlalchemy import Column, String, Text, Integer, Float, DateTime
from core.database import Base
import datetime


class MasteryLedger(Base):
    """Tracks mastery of individual concepts across sessions."""

    __tablename__ = 'mastery_ledger'

    concept_id = Column(String, primary_key=True)
    persona_id = Column(String, nullable=False, index=True)
    concept_key = Column(String, nullable=False)
    concept_label = Column(String, nullable=False)
    status = Column(String, default='encountered')
    mastery_score = Column(Float, default=0.0)
    encounter_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    sessions_tested = Column(Text, default='[]')
    first_seen = Column(String, default='')
    last_tested = Column(String, default='')
    vault_sources = Column(Text, default='[]')
    mentor_notes = Column(Text, nullable=True)


class MasteryCertificate(Base):
    """Proof of Mastery certification record."""

    __tablename__ = 'mastery_certificates'

    cert_id = Column(String, primary_key=True)
    persona_id = Column(String, nullable=False, index=True)
    concept_key = Column(String, nullable=False)
    concept_label = Column(String, nullable=False)
    issued_at = Column(String, nullable=False)
    mentor_statement = Column(Text, nullable=False)
    evidence_summary = Column(Text, default='{}')
    cert_json_path = Column(String, default='')
    delivered = Column(Integer, default=0)
