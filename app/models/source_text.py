from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.teacher import PyObjectId


class SourceTextBase(BaseModel):
    title: str
    content: str
    type: str  # comptine, dialogue, récit, etc.
    grade: str  # CP, CE1, CE2, CM1, CM2
    tags: List[str] = []
    difficulty: int  # 1-5
    teacherId: PyObjectId
    isActive: bool = True

class SourceTextCreate(SourceTextBase):
    pass

class SourceTextUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    grade: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty: Optional[int] = None
    isActive: Optional[bool] = None

class SourceTextInDBBase(SourceTextBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    submittedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SourceText(SourceTextInDBBase):
    pass