from typing import List, Optional
from bson import ObjectId
from app.db.repositories.base_repository import BaseRepository
from app.models.answer_template import AnswerTemplate, AnswerTemplateCreate, AnswerTemplateUpdate


class AnswerTemplateRepository(BaseRepository[AnswerTemplate]):
    def __init__(self):
        super().__init__("answer_templates", AnswerTemplate)

    async def create_template(self, template_in: AnswerTemplateCreate) -> AnswerTemplate:
        """Crée un nouveau modèle de réponse."""
        template_dict = template_in.dict()
        return await self.create(template_dict)

    async def update_template(self, template_id: str, template_in: AnswerTemplateUpdate) -> Optional[AnswerTemplate]:
        """Met à jour un modèle de réponse existant."""
        template_dict = template_in.dict(exclude_unset=True)
        return await self.update(template_id, template_dict)

    async def get_by_question(self, question_id: str) -> List[AnswerTemplate]:
        """Récupère tous les modèles de réponse pour une question spécifique."""
        cursor = self.collection.find({"questionId": ObjectId(question_id)})
        documents = await cursor.to_list(length=100)
        return [AnswerTemplate(**doc) for doc in documents]