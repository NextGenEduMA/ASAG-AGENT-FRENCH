from typing import List, Optional
from bson import ObjectId
from app.db.repositories.base_repository import BaseRepository
from app.models.teacher import Teacher, TeacherCreate, TeacherUpdate, TeacherInDB
from app.core.security import get_password_hash


class TeacherRepository(BaseRepository[Teacher]):
    def __init__(self):
        super().__init__("teachers", Teacher)

    async def create_teacher(self, teacher_in: TeacherCreate) -> Teacher:
        """Crée un nouvel enseignant."""
        teacher_dict = teacher_in.dict(exclude={"password"})
        teacher_dict["hashed_password"] = get_password_hash(teacher_in.password)

        return await self.create(teacher_dict)

    async def update_teacher(self, teacher_id: str, teacher_in: TeacherUpdate) -> Optional[Teacher]:
        """Met à jour un enseignant existant."""
        teacher_dict = teacher_in.dict(exclude_unset=True)

        # Si le mot de passe est fourni, le hacher
        if "password" in teacher_dict:
            teacher_dict["hashed_password"] = get_password_hash(teacher_dict.pop("password"))

        return await self.update(teacher_id, teacher_dict)

    async def get_by_email(self, email: str) -> Optional[TeacherInDB]:
        """Récupère un enseignant par son email."""
        document = await self.collection.find_one({"email": email})
        if document:
            return TeacherInDB(**document)
        return None

    async def update_last_login(self, teacher_id: str) -> bool:
        """Met à jour la date de dernière connexion."""
        from datetime import datetime

        result = await self.collection.update_one(
            {"_id": ObjectId(teacher_id)},
            {"$set": {"lastLogin": datetime.utcnow()}}
        )

        return result.modified_count > 0