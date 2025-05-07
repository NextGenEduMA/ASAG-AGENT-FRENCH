from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.teacher import PyObjectId

class ClassGroupBase(BaseModel):
    groupName: str
    teacherId: PyObjectId
    grade: str  # CP, CE1, CE2, CM1, CM2
    academicYear: str
    studentCount: int = 0

class ClassGroupCreate(ClassGroupBase):
    pass

class ClassGroupUpdate(BaseModel):
    groupName: Optional[str] = None
    teacherId: Optional[PyObjectId] = None
    grade: Optional[str] = None
    academicYear: Optional[str] = None
    studentCount: Optional[int] = None

class ClassGroupInDBBase(ClassGroupBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ClassGroup(ClassGroupInDBBase):
    pass

class ClassGroupWithStudents(ClassGroup):
    students: List[PyObjectId] = []