from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.teacher import PyObjectId

class OpenQuestionBase(BaseModel):
    textId: PyObjectId
    questionText: str
    questionType: str  # compréhension, grammaire, vocabulaire, etc.
    difficultyLevel: int  # 1-5
    skills: List[str] = []  # compétences évaluées
    grade: str  # CP, CE1, CE2, CM1, CM2
    maxScore: int
    creationMethod: str = "auto-generated"  # auto-generated, teacher-modified
    isActive: bool = True

class OpenQuestionCreate(OpenQuestionBase):
    pass

class OpenQuestionUpdate(BaseModel):
    questionText: Optional[str] = None
    questionType: Optional[str] = None
    difficultyLevel: Optional[int] = None
    skills: Optional[List[str]] = None
    grade: Optional[str] = None
    maxScore: Optional[int] = None
    creationMethod: Optional[str] = None
    isActive: Optional[bool] = None

class OpenQuestionInDBBase(OpenQuestionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class OpenQuestion(OpenQuestionInDBBase):
    pass