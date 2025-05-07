from typing import List, Optional
from bson import ObjectId
from app.db.repositories.base_repository import BaseRepository
from app.models.student_answer import StudentAnswer, StudentAnswerCreate, StudentAnswerUpdate


class StudentAnswerRepository(BaseRepository[StudentAnswer]):
    def __init__(self):
        super().__init__("student_answers", StudentAnswer)

    async def create_answer(self, answer_in: StudentAnswerCreate) -> StudentAnswer:
        """Crée une nouvelle réponse d'élève."""
        answer_dict = answer_in.dict()
        return await self.create(answer_dict)

    async def update_answer(self, answer_id: str, answer_in: StudentAnswerUpdate) -> Optional[StudentAnswer]:
        """Met à jour une réponse d'élève existante."""
        answer_dict = answer_in.dict(exclude_unset=True)
        return await self.update(answer_id, answer_dict)

    async def get_by_student(self, student_id: str) -> List[StudentAnswer]:
        """Récupère toutes les réponses pour un élève spécifique."""
        cursor = self.collection.find({"studentId": ObjectId(student_id)})
        documents = await cursor.to_list(length=100)
        return [StudentAnswer(**doc) for doc in documents]

    async def get_by_question(self, question_id: str) -> List[StudentAnswer]:
        """Récupère toutes les réponses pour une question spécifique."""
        cursor = self.collection.find({"questionId": ObjectId(question_id)})
        documents = await cursor.to_list(length=100)
        return [StudentAnswer(**doc) for doc in documents]

    async def get_by_student_and_question(self, student_id: str, question_id: str) -> List[StudentAnswer]:
        """Récupère toutes les réponses d'un élève pour une question spécifique."""
        cursor = self.collection.find({
            "studentId": ObjectId(student_id),
            "questionId": ObjectId(question_id)
        })
        documents = await cursor.to_list(length=100)
        return [StudentAnswer(**doc) for doc in documents]

    async def get_latest_attempt(self, student_id: str, question_id: str) -> Optional[StudentAnswer]:
        """Récupère la dernière tentative d'un élève pour une question spécifique."""
        cursor = self.collection.find({
            "studentId": ObjectId(student_id),
            "questionId": ObjectId(question_id)
        }).sort("submittedAt", -1).limit(1)

        documents = await cursor.to_list(length=1)
        if documents:
            return StudentAnswer(**documents[0])
        return None
