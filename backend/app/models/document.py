import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False) # in bytes
    mime_type = Column(String, nullable=False)
    sha256_hash = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="UPLOADED", nullable=False) # UPLOADED, QUEUED, PROCESSING, COMPLETED, FAILED
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)