from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.db.repositories.base_repository import BaseRepository
from app.models.source_text import SourceText, SourceTextCreate, SourceTextUpdate


class TextRepository(BaseRepository[SourceText]):
    def __init__(self):
        super().__init__("source_texts", SourceText)

    async def create_text(self, text_in: SourceTextCreate) -> SourceText:
        """Crée un nouveau texte source."""
        text_dict = text_in.dict()
        return await self.create(text_dict)

    async def update_text(self, text_id: str, text_in: SourceTextUpdate) -> Optional[SourceText]:
        """Met à jour un texte source existant."""
        text_dict = text_in.dict(exclude_unset=True)
        return await self.update(text_id, text_dict)

    async def get_by_teacher(self, teacher_id: str) -> List[SourceText]:
        """Récupère tous les textes soumis par un enseignant spécifique."""
        cursor = self.collection.find({"teacherId": ObjectId(teacher_id)})
        documents = await cursor.to_list(length=100)
        return [SourceText(**doc) for doc in documents]

    async def get_by_grade(self, grade: str) -> List[SourceText]:
        """Récupère tous les textes pour un niveau scolaire spécifique."""
        cursor = self.collection.find({"grade": grade, "isActive": True})
        documents = await cursor.to_list(length=100)
        return [SourceText(**doc) for doc in documents]

    async def get_active_texts(self) -> List[SourceText]:
        """Récupère tous les textes actifs."""
        cursor = self.collection.find({"isActive": True})
        documents = await cursor.to_list(length=100)
        return [SourceText(**doc) for doc in documents]