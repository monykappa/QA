from datetime import datetime
import pytz
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from database import SessionLocal
from models import CategoryDB, QAItemDB
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
    if not qa.category or qa.category.strip() == "":
        raise HTTPException(status_code=400, detail="Category is required")
    
    # Verify category exists
    existing_category = db.query(CategoryDB).filter(CategoryDB.name == qa.category).first()
    if not existing_category:
        raise HTTPException(status_code=400, detail="Category does not exist")

    # Get current time in Phnom Penh
    created_at = datetime.now(pytz.timezone('Asia/Phnom_Penh'))
    print(f"Submitting Q&A with timestamp: {created_at}")  # Debug log

    qa_item = QAItemDB(
        question=qa.question,
        answer=qa.answer,
        category=qa.category,
        created_at=created_at,
        updated_timestamp=None
    )
    db.add(qa_item)
    db.commit()
    db.refresh(qa_item)
    return {
        "message": "Question and answer saved successfully!", 
        "id": qa_item.id,
        "created_at": format_timestamp(qa_item.created_at)
    }

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
        # Get current time in Phnom Penh
        timestamp = datetime.now(pytz.timezone('Asia/Phnom_Penh'))
        print(f"Updating Q&A with timestamp: {timestamp}")  # Debug log
        item.updated_timestamp = timestamp
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
            "created_at": format_timestamp(item.created_at),
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
            "created_at": format_timestamp(item.created_at),
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