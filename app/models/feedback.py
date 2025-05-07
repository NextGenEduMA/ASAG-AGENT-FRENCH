from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.teacher import PyObjectId

class FeedbackBase(BaseModel):
    answerId: PyObjectId
    feedbackContent: str
    correctionDetails: Dict[str, Any] = {}
    suggestedImprovements: List[str] = []
    positivePoints: List[str] = []
    feedbackType: str = "corrective"  # encouragement, corrective, explicative
    wasHelpful: Optional[bool] = None

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    feedbackContent: Optional[str] = None
    correctionDetails: Optional[Dict[str, Any]] = None
    suggestedImprovements: Optional[List[str]] = None
    positivePoints: Optional[List[str]] = None
    feedbackType: Optional[str] = None
    wasHelpful: Optional[bool] = None

class FeedbackInDBBase(FeedbackBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    generatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Feedback(FeedbackInDBBase):
    pass