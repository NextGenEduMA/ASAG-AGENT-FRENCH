from typing import List, Optional
from bson import ObjectId
from app.db.repositories.base_repository import BaseRepository
from app.models.student import Student, StudentCreate, StudentUpdate


class StudentRepository(BaseRepository[Student]):
    def __init__(self):
        super().__init__("students", Student)

    async def create_student(self, student_in: StudentCreate) -> Student:
        """Crée un nouvel élève."""
        student_dict = student_in.dict()
        return await self.create(student_dict)

    async def update_student(self, student_id: str, student_in: StudentUpdate) -> Optional[Student]:
        """Met à jour un élève existant."""
        student_dict = student_in.dict(exclude_unset=True)
        return await self.update(student_id, student_dict)

    async def get_by_group(self, group_id: str) -> List[Student]:
        """Récupère tous les élèves d'un groupe spécifique."""
        # Cette méthode nécessite une collection séparée pour les associations élève-groupe
        # Pour simplifier, nous utilisons une approche basique
        cursor = self.collection.find({"groupIds": ObjectId(group_id)})
        documents = await cursor.to_list(length=100)
        return [Student(**doc) for doc in documents]

    async def update_progress(self, student_id: str, progress_level: float) -> bool:
        """Met à jour le niveau de progression d'un élève."""
        result = await self.collection.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": {"progressLevel": progress_level}}
        )
        return result.modified_count > 0

    async def update_learning_profile(self, student_id: str, learning_profile: dict) -> bool:
        """Met à jour le profil d'apprentissage d'un élève."""
        result = await self.collection.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": {"learningProfile": learning_profile}}
        )
        return result.modified_count > 0