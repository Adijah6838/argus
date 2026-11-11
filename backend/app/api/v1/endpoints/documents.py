import os
import uuid
import hashlib
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import SessionLocal
from app.models.user import User
from app.models.document import Document
from app.models.extracted_text import ExtractedText
from app.models.extracted_entity import ExtractedEntity
from app.schemas.document import DocumentResponse
from app.api.v1.endpoints.auth import get_current_user
from app.workers.tasks import process_document

router = APIRouter()
UPLOAD_DIR = "/app/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 20 * 1024 * 1024

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 20MB limit.")
    
    sha256_hash = hashlib.sha256(file_bytes).hexdigest()
    if db.query(Document).filter(Document.sha256_hash == sha256_hash).first():
        raise HTTPException(status_code=409, detail="Duplicate document detected.")

    stored_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    new_doc = Document(
        user_id=current_user.id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_size=len(file_bytes),
        mime_type=file.content_type,
        sha256_hash=sha256_hash,
        status="QUEUED"
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    process_document.delay(str(new_doc.id))
    return new_doc

@router.get("/", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Document).filter(Document.user_id == current_user.id).all()

@router.post("/{document_id}/process")
def trigger_processing(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc.status = "QUEUED"
    db.commit()
    process_document.delay(document_id)
    return {"message": "Processing queued."}

@router.get("/{document_id}/extracted-text")
def get_extracted_text(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    text_record = db.query(ExtractedText).filter(ExtractedText.document_id == document_id).first()
    if not text_record:
        raise HTTPException(status_code=404, detail="Text not extracted yet.")
    
    return {"document_id": document_id, "content": text_record.content}

@router.get("/{document_id}/entities")
def get_extracted_entities(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    entities = db.query(ExtractedEntity).filter(ExtractedEntity.document_id == document_id).all()
    return [
        {"id": str(e.id), "type": e.entity_type, "value": e.entity_value, "confidence": e.confidence}
        for e in entities
    ]

@router.get("/compare/{doc_a_id}/{doc_b_id}")
def compare_documents(doc_a_id: str, doc_b_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.comparison import DocumentComparer
    
    entities_a = db.query(ExtractedEntity).filter(ExtractedEntity.document_id == doc_a_id).all()
    entities_b = db.query(ExtractedEntity).filter(ExtractedEntity.document_id == doc_b_id).all()

    if not entities_a or not entities_b:
        raise HTTPException(status_code=400, detail="Both documents must have extracted entities to compare.")

    def group_entities(ents):
        grouped = {}
        for e in ents:
            if e.entity_type not in grouped:
                grouped[e.entity_type] = []
            grouped[e.entity_type].append(e.entity_value)
        return grouped

    grouped_a = group_entities(entities_a)
    grouped_b = group_entities(entities_b)

    result = DocumentComparer.compare(grouped_a, grouped_b)
    return result

@router.get("/search/query")
def search_documents(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # PostgreSQL Full-Text Search
    # This ranks results based on relevance (ts_rank)
    search_query = text("""
        SELECT d.id, d.original_filename, d.created_at, et.content,
               ts_headline('english', et.content, plainto_tsquery('english', :query), 'StartSel=<mark>, StopSel=</mark>') as highlighted_content
        FROM documents d
        JOIN extracted_texts et ON d.id = et.document_id
        WHERE d.user_id = :user_id
          AND to_tsvector('english', et.content) @@ plainto_tsquery('english', :query)
        ORDER BY ts_rank(to_tsvector('english', et.content), plainto_tsquery('english', :query)) DESC
        LIMIT 10
    """)
    
    results = db.execute(search_query, {"user_id": str(current_user.id), "query": q}).fetchall()
    
    return [
        {
            "id": str(row.id),
            "filename": row.original_filename,
            "created_at": row.created_at,
            "highlighted_content": row.highlighted_content
        }
        for row in results
    ]