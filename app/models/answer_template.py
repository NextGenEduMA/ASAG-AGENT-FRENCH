from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.teacher import PyObjectId

class AnswerTemplateBase(BaseModel):
    questionId: Optional[PyObjectId] = None  # Rendre ce champ optionnel
    modelAnswer: str
    keyElements: List[str] = []
    acceptableSynonyms: List[str] = []
    scoringRubric: Dict[str, Any] = {}
    minimumScore: float = 0.0
    requiresGrammarCheck: bool = True

class AnswerTemplateCreate(AnswerTemplateBase):
    pass

class AnswerTemplateUpdate(BaseModel):
    modelAnswer: Optional[str] = None
    keyElements: Optional[List[str]] = None
    acceptableSynonyms: Optional[List[str]] = None
    scoringRubric: Optional[Dict[str, Any]] = None
    minimumScore: Optional[float] = None
    requiresGrammarCheck: Optional[bool] = None

class AnswerTemplateInDBBase(AnswerTemplateBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AnswerTemplate(AnswerTemplateInDBBase):
    pass
