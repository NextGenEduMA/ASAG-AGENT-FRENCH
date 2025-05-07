from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.db.repositories.base_repository import BaseRepository
from app.models.open_question import OpenQuestion, OpenQuestionCreate, OpenQuestionUpdate


class QuestionRepository(BaseRepository[OpenQuestion]):
    def __init__(self):
        super().__init__("open_questions", OpenQuestion)

    async def create_question(self, question_in: OpenQuestionCreate) -> OpenQuestion:
        """Crée une nouvelle question ouverte."""
        question_dict = question_in.dict()
        return await self.create(question_dict)

    async def update_question(self, question_id: str, question_in: OpenQuestionUpdate) -> Optional[OpenQuestion]:
        """Met à jour une question ouverte existante."""
        question_dict = question_in.dict(exclude_unset=True)
        return await self.update(question_id, question_dict)

    async def get_by_text(self, text_id: str) -> List[OpenQuestion]:
        """Récupère toutes les questions pour un texte source spécifique."""
        cursor = self.collection.find({"textId": ObjectId(text_id), "isActive": True})
        documents = await cursor.to_list(length=100)
        return [OpenQuestion(**doc) for doc in documents]

    async def get_by_grade_and_type(self, grade: str, question_type: str) -> List[OpenQuestion]:
        """Récupère toutes les questions pour un niveau et un type spécifiques."""
        cursor = self.collection.find({"grade": grade, "questionType": question_type, "isActive": True})
        documents = await cursor.to_list(length=100)
        return [OpenQuestion(**doc) for doc in documents]

    async def get_by_difficulty(self, min_difficulty: int, max_difficulty: int) -> List[OpenQuestion]:
        """Récupère les questions dans une plage de difficulté."""
        cursor = self.collection.find({
            "difficultyLevel": {"$gte": min_difficulty, "$lte": max_difficulty},
            "isActive": True
        })
        documents = await cursor.to_list(length=100)
        return [OpenQuestion(**doc) for doc in documents]
