from datetime import datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from database import SessionLocal
from models import QAItemDB
from schemas import QASubmit, QAUpdate, QAItem
from utils import format_timestamp

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/submit_qa/", summary="Submit a new question and answer", tags=["Q&A"])
async def submit_qa(qa: QASubmit, db: Session = Depends(get_db)):
    qa_item = QAItemDB(
        question=qa.question,
        answer=qa.answer,
        category=qa.category,
        timestamp=datetime.now(),
        updated_timestamp=None
    )
    db.add(qa_item)
    db.commit()
    db.refresh(qa_item)
    return {"message": "Question and answer saved successfully!", "id": qa_item.id}

@router.put("/{qa_id}", summary="Update a Q&A pair by ID", tags=["Q&A"])
async def update_qa(qa_id: int, qa: QAUpdate, db: Session = Depends(get_db)):
    item = db.query(QAItemDB).filter(QAItemDB.id == qa_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Q&A pair not found")
    
    updated = False
    if qa.question is not None:
        item.question = qa.question
        updated = True
    if qa.answer is not None:
        item.answer = qa.answer
        updated = True
    if qa.category is not None:
        item.category = qa.category
        updated = True
    
    if updated:
        item.updated_timestamp = datetime.now()
        db.commit()
        db.refresh(item)
    
    return {"message": "Q&A pair updated successfully!" if updated else "No updates provided."}

@router.get("/", summary="Retrieve all Q&A pairs", tags=["Q&A"])
async def get_qa(db: Session = Depends(get_db)):
    items = db.query(QAItemDB).all()
    if not items:
        return []
    return [
        {
            "id": item.id,
            "question": item.question,
            "answer": item.answer,
            "category": item.category,
            "timestamp": format_timestamp(item.timestamp),
            "updated_timestamp": format_timestamp(item.updated_timestamp)
        }
        for item in items
    ]

@router.get("/{qa_id}", summary="Retrieve a specific Q&A pair by ID", tags=["Q&A"])
async def get_qa_by_id(qa_id: int, db: Session = Depends(get_db)):
    item = db.query(QAItemDB).filter(QAItemDB.id == qa_id).first()
    if item:
        return {
            "id": item.id,
            "question": item.question,
            "answer": item.answer,
            "category": item.category,
            "timestamp": format_timestamp(item.timestamp),
            "updated_timestamp": format_timestamp(item.updated_timestamp)
        }
    raise HTTPException(status_code=404, detail="Q&A pair not found")

@router.delete("/{qa_id}", summary="Delete a Q&A pair by ID", tags=["Q&A"])
async def delete_qa(qa_id: int, db: Session = Depends(get_db)):
    item = db.query(QAItemDB).filter(QAItemDB.id == qa_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Q&A pair not found")
    db.delete(item)
    db.commit()
    return {"message": "Q&A pair deleted successfully!"}