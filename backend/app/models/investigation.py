import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="OPEN", nullable=False) # OPEN, IN_PROGRESS, COMPLETED, ARCHIVED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class InvestigationDocument(Base):
    __tablename__ = "investigation_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    investigation_id = Column(UUID(as_uuid=True), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

class InvestigationNote(Base):
    __tablename__ = "investigation_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    investigation_id = Column(UUID(as_uuid=True), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)