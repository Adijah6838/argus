import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class ExtractedEntity(Base):
    __tablename__ = "extracted_entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True) # email, date, amount, organization
    entity_value = Column(String, nullable=False)
    confidence = Column(Float, default=1.0)
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)