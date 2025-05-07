from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.teacher import PyObjectId

class StudentAnswerBase(BaseModel):
    studentId: PyObjectId
    questionId: PyObjectId
    answerText: str
    submissionMethod: str = "text"  # text, handwriting
    scoreObtained: float = 0.0
    answerStatus: str = "pending"  # pending, correct, partially_correct, incorrect
    attemptNumber: int = 1
    timeSpent: int = 0  # in seconds

class StudentAnswerCreate(StudentAnswerBase):
    pass

class StudentAnswerUpdate(BaseModel):
    answerText: Optional[str] = None
    scoreObtained: Optional[float] = None
    answerStatus: Optional[str] = None
    attemptNumber: Optional[int] = None
    timeSpent: Optional[int] = None

class StudentAnswerInDBBase(StudentAnswerBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    submittedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class StudentAnswer(StudentAnswerInDBBase):
    pass