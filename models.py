from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class QAItemDB(Base):
    __tablename__ = "qa_items"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question = Column(String)   
    answer = Column(String)
    category = Column(String)
    created_at = Column(DateTime, nullable=False)  # Make sure it's not nullable
    updated_timestamp = Column(DateTime, nullable=True)

class CategoryDB(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)