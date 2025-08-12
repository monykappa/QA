from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from database import SessionLocal
from models import QAItemDB
from utils import format_timestamp
import csv
import io
import json
import os
from datetime import datetime

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/csv", summary="Export all Q&A pairs as CSV", tags=["Exports"])
async def export_csv(db: Session = Depends(get_db)):
    items = db.query(QAItemDB).all()
    
    if not items:
        raise HTTPException(status_code=404, detail="No Q&A pairs available to export")
    
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["id", "question", "answer", "category", "timestamp", "updated_timestamp"],
        lineterminator="\n"
    )
    writer.writeheader()
    for item in items:
        writer.writerow({
            "id": item.id,
            "question": item.question,
            "answer": item.answer,
            "category": item.category,
            "timestamp": format_timestamp(item.timestamp),
            "updated_timestamp": format_timestamp(item.updated_timestamp)
        })
    csv_content = output.getvalue()
    output.close()
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"qa_export_{timestamp_str}.csv"
    os.makedirs("exports", exist_ok=True)
    with open(os.path.join("exports", csv_filename), "w", encoding="utf-8") as f:
        f.write(csv_content)
    
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={csv_filename}"}
    )

@router.get("/json", summary="Export all Q&A pairs as JSON", tags=["Exports"])
async def export_json(db: Session = Depends(get_db)):
    items = db.query(QAItemDB).all()
    
    if not items:
        raise HTTPException(status_code=404, detail="No Q&A pairs available to export")
    
    data = [
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
    json_content = json.dumps(data, indent=2)
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"qa_export_{timestamp_str}.json"
    os.makedirs("exports", exist_ok=True)
    with open(os.path.join("exports", json_filename), "w", encoding="utf-8") as f:
        f.write(json_content)
    
    return StreamingResponse(
        iter([json_content]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={json_filename}"}
    )