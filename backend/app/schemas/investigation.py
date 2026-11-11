from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class InvestigationCreate(BaseModel):
    title: str
    description: Optional[str] = None

class NoteCreate(BaseModel):
    content: str

class InvestigationResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True