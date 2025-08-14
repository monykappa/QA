from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from database import SessionLocal
from models import CategoryDB, QAItemDB
from schemas import CategorySubmit, CategoryItem

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", summary="Add a new category", tags=["Categories"])
async def add_category(category: CategorySubmit, db: Session = Depends(get_db)):
    # Check if category already exists
    existing_category = db.query(CategoryDB).filter(CategoryDB.name == category.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    new_category = CategoryDB(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return {"message": "Category added successfully!", "id": new_category.id, "name": new_category.name}

@router.put("/{category_id}", summary="Update a category by ID", tags=["Categories"])
async def update_category(category_id: int, category: CategorySubmit, db: Session = Depends(get_db)):
    # Find the category to update
    item = db.query(CategoryDB).filter(CategoryDB.id == category_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if the new name already exists (excluding the current category)
    existing_category = db.query(CategoryDB).filter(CategoryDB.name == category.name, CategoryDB.id != category_id).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    # Update the category name
    item.name = category.name
    db.commit()
    db.refresh(item)
    return {"message": "Category updated successfully!", "id": item.id, "name": item.name}

@router.delete("/{category_id}", summary="Delete a category by ID", tags=["Categories"])
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    # Find the category
    item = db.query(CategoryDB).filter(CategoryDB.id == category_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if the category is used by any Q&A items
    qa_items = db.query(QAItemDB).filter(QAItemDB.category == item.name).first()
    if qa_items:
        raise HTTPException(status_code=400, detail="Cannot delete category; it is in use by Q&A items")
    
    # Delete the category
    db.delete(item)
    db.commit()
    return {"message": "Category deleted successfully!"}

@router.get("/", summary="Retrieve all unique categories", tags=["Categories"])
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(CategoryDB).all()
    return [{"id": category.id, "name": category.name} for category in categories if category.name is not None]