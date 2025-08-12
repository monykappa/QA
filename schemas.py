from pydantic import BaseModel, constr, Field
from typing import Optional
from datetime import datetime

class QASubmit(BaseModel):
    question: constr(min_length=1)  # Removed max_length
    answer: constr(min_length=1)    # Removed max_length
    category: constr(min_length=1)  # Category accepts any string

class QAUpdate(BaseModel):
    question: Optional[constr(min_length=1)] = None
    answer: Optional[constr(min_length=1)] = None
    category: Optional[constr(min_length=1)] = None

class QAItem(BaseModel):
    id: int = Field(default=None)
    question: constr(min_length=1)  # Removed max_length
    answer: constr(min_length=1)    # Removed max_length
    category: constr(min_length=1)
    timestamp: datetime
    updated_timestamp: Optional[datetime] = None

class CategorySubmit(BaseModel):
    name: constr(min_length=1)  # Category name must not be empty

class CategoryItem(BaseModel):
    id: int = Field(default=None)
    name: constr(min_length=1)