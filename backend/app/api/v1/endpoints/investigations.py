from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.models.investigation import Investigation, InvestigationDocument, InvestigationNote
from app.models.document import Document
from app.schemas.investigation import InvestigationCreate, InvestigationResponse, NoteCreate
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/", response_model=InvestigationResponse)
def create_investigation(
    inv_in: InvestigationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = Investigation(
        user_id=current_user.id,
        title=inv_in.title,
        description=inv_in.description
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv

@router.get("/", response_model=List[InvestigationResponse])
def list_investigations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Investigation).filter(Investigation.user_id == current_user.id).all()

@router.post("/{inv_id}/documents/{doc_id}")
def attach_document(
    inv_id: str, doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = db.query(Investigation).filter(Investigation.id == inv_id, Investigation.user_id == current_user.id).first()
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    
    if not inv or not doc:
        raise HTTPException(status_code=404, detail="Investigation or Document not found")

    existing = db.query(InvestigationDocument).filter_by(investigation_id=inv_id, document_id=doc_id).first()
    if not existing:
        link = InvestigationDocument(investigation_id=inv.id, document_id=doc.id)
        db.add(link)
        db.commit()
    
    return {"message": "Document attached to investigation"}

@router.post("/{inv_id}/notes")
def add_note(
    inv_id: str, note_in: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = db.query(Investigation).filter(Investigation.id == inv_id, Investigation.user_id == current_user.id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    note = InvestigationNote(investigation_id=inv.id, content=note_in.content)
    db.add(note)
    db.commit()
    return {"message": "Note added successfully"}
from fastapi import Response
from app.models.extracted_entity import ExtractedEntity
from app.services.report_generator import ReportGenerator

@router.get("/{inv_id}/report/{format}")
def generate_report(
    inv_id: str, format: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = db.query(Investigation).filter(Investigation.id == inv_id, Investigation.user_id == current_user.id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    # Gather Data
    notes = db.query(InvestigationNote).filter(InvestigationNote.investigation_id == inv.id).all()
    inv_docs = db.query(InvestigationDocument).filter(InvestigationDocument.investigation_id == inv.id).all()
    
    documents_data = []
    for inv_doc in inv_docs:
        doc = db.query(Document).filter(Document.id == inv_doc.document_id).first()
        entities = db.query(ExtractedEntity).filter(ExtractedEntity.document_id == doc.id).all()
        documents_data.append({
            "filename": doc.original_filename,
            "entities": [{"type": e.entity_type, "value": e.entity_value} for e in entities]
        })

    report_data = {
        "title": inv.title,
        "status": inv.status,
        "created_at": inv.created_at.strftime("%Y-%m-%d %H:%M"),
        "description": inv.description,
        "notes": [{"content": n.content, "created_at": n.created_at.strftime("%Y-%m-%d")} for n in notes],
        "documents": documents_data
    }

    # Generate Output
    if format == "json":
        json_str = ReportGenerator.generate_json_report(report_data)
        return Response(content=json_str, media_type="application/json", headers={
            "Content-Disposition": f"attachment; filename=report_{inv.id}.json"
        })
    elif format == "pdf":
        pdf_bytes = ReportGenerator.generate_pdf_report(report_data)
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename=report_{inv.id}.pdf"
        })
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'json' or 'pdf'.")