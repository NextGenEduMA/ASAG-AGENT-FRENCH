from typing import List, Optional
from bson import ObjectId
from app.db.repositories.base_repository import BaseRepository
from app.models.feedback import Feedback, FeedbackCreate, FeedbackUpdate


class FeedbackRepository(BaseRepository[Feedback]):
    def __init__(self):
        super().__init__("feedbacks", Feedback)

    async def create_feedback(self, feedback_in: FeedbackCreate) -> Feedback:
        """Crée un nouveau feedback."""
        feedback_dict = feedback_in.dict()
        return await self.create(feedback_dict)

    async def update_feedback(self, feedback_id: str, feedback_in: FeedbackUpdate) -> Optional[Feedback]:
        """Met à jour un feedback existant."""
        feedback_dict = feedback_in.dict(exclude_unset=True)
        return await self.update(feedback_id, feedback_dict)

    async def get_by_answer(self, answer_id: str) -> List[Feedback]:
        """Récupère tous les feedbacks pour une réponse spécifique."""
        cursor = self.collection.find({"answerId": ObjectId(answer_id)})
        documents = await cursor.to_list(length=100)
        return [Feedback(**doc) for doc in documents]

    async def get_latest_feedback(self, answer_id: str) -> Optional[Feedback]:
        """Récupère le dernier feedback pour une réponse spécifique."""
        cursor = self.collection.find({"answerId": ObjectId(answer_id)}).sort("generatedAt", -1).limit(1)

        documents = await cursor.to_list(length=1)
        if documents:
            return Feedback(**documents[0])
        return None