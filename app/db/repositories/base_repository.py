from typing import Any, Dict, List, Optional, Generic, TypeVar, Type
from pydantic import BaseModel
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.db.mongodb import mongodb

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Classe de base pour tous les repositories."""

    def __init__(self, collection_name: str, model: Type[ModelType]):
        self.collection_name = collection_name
        self.model = model

    @property
    def collection(self) -> AsyncIOMotorCollection:
        return mongodb.db[self.collection_name]

    async def get(self, id: str) -> Optional[ModelType]:
        """Récupère un document par son ID."""
        document = await self.collection.find_one({"_id": ObjectId(id)})
        if document:
            return self.model(**document)
        return None

    async def get_all(self) -> List[ModelType]:
        """Récupère tous les documents."""
        cursor = self.collection.find()
        documents = await cursor.to_list(length=100)
        return [self.model(**doc) for doc in documents]

    async def create(self, model_data: Dict[str, Any]) -> ModelType:
        """Crée un nouveau document."""
        result = await self.collection.insert_one(model_data)
        document = await self.collection.find_one({"_id": result.inserted_id})
        return self.model(**document)

    async def update(self, id: str, model_data: Dict[str, Any]) -> Optional[ModelType]:
        """Met à jour un document existant."""
        await self.collection.update_one(
            {"_id": ObjectId(id)}, {"$set": model_data}
        )
        return await self.get(id)

    async def delete(self, id: str) -> bool:
        """Supprime un document."""
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0