"""SQLAlchemy models for mastery ledger and mastery certificates."""

from sqlalchemy import Column, Integer, Text, Float

from core.database import Base


class MasteryLedger(Base):
    """Cross-session concept mastery record for a persona."""

    __tablename__ = "mastery_ledger"

    concept_id = Column(Text, primary_key=True)
    persona_id = Column(Text, nullable=False, index=True)
    concept_key = Column(Text, nullable=False, index=True)
    concept_label = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    mastery_score = Column(Float, nullable=False, default=0.0)
    encounter_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failure_count = Column(Integer, nullable=False, default=0)
    sessions_tested = Column(Text, nullable=False, default="[]")
    vault_sources = Column(Text, nullable=False, default="[]")
    last_tested = Column(Text, nullable=True)


class MasteryCertificate(Base):
    """Issued certification proving concept mastery."""

    __tablename__ = "mastery_certificates"

    cert_id = Column(Text, primary_key=True)
    persona_id = Column(Text, nullable=False, index=True)
    concept_key = Column(Text, nullable=False)
    concept_label = Column(Text, nullable=False)
    issued_at = Column(Text, nullable=False)
    mentor_statement = Column(Text, nullable=False)
    evidence_summary = Column(Text, nullable=False)
    cert_json_path = Column(Text, nullable=False)
    delivered = Column(Integer, nullable=False, default=0)
