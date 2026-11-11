from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class DocumentResponse(BaseModel):
    id: UUID
    original_filename: str
    file_size: int
    mime_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True