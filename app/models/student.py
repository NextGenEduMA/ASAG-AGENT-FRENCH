from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.teacher import PyObjectId

class StudentBase(BaseModel):
    firstName: str
    lastName: str
    age: int
    grade: str  # CP, CE1, CE2, CM1, CM2
    profileAvatar: Optional[str] = None
    progressLevel: float = 0.0

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    age: Optional[int] = None
    grade: Optional[str] = None
    profileAvatar: Optional[str] = None
    progressLevel: Optional[float] = None
    learningProfile: Optional[Dict[str, Any]] = None

class StudentInDBBase(StudentBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    learningProfile: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Student(StudentInDBBase):
    pass