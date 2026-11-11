import os
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.extracted_text import ExtractedText
from app.models.extracted_entity import ExtractedEntity
from app.services.extraction import TextExtractor
from app.services.entity_recognition import EntityExtractor

@celery_app.task(name="process_document")
def process_document(document_id: str):
    db = SessionLocal()
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        return {"error": "Document not found"}

    doc.status = "PROCESSING"
    db.commit()

    try:
        # 1. Extract text
        file_path = os.path.join("/app/data/uploads", doc.stored_filename)
        extracted_content = TextExtractor.extract_text(file_path, doc.mime_type)

        # 2. Save extracted text
        db.query(ExtractedText).filter(ExtractedText.document_id == doc.id).delete()
        text_record = ExtractedText(document_id=doc.id, content=extracted_content)
        db.add(text_record)
        
        # 3. Extract and save entities
        db.query(ExtractedEntity).filter(ExtractedEntity.document_id == doc.id).delete()
        entities = EntityExtractor.extract_entities(extracted_content)
        for entity in entities:
            new_entity = ExtractedEntity(
                document_id=doc.id,
                entity_type=entity["type"],
                entity_value=entity["value"],
                confidence=entity["confidence"]
            )
            db.add(new_entity)
        
        doc.status = "COMPLETED"
        db.commit()
        return {"status": "success", "document_id": document_id, "entities_found": len(entities)}

    except Exception as e:
        db.rollback()
        doc.status = "FAILED"
        db.commit()
        return {"status": "error", "message": str(e), "document_id": document_id}
    finally:
        db.close()