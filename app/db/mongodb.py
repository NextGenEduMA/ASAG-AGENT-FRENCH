from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Connecte l'application à la base de données MongoDB."""
    logger.info("Connexion à MongoDB...")
    mongodb.client = AsyncIOMotorClient(settings.MONGO_URI)
    mongodb.db = mongodb.client[settings.MONGO_DB_NAME]
    logger.info("Connexion à MongoDB établie avec succès")

async def close_mongo_connection():
    """Ferme la connexion à MongoDB."""
    logger.info("Fermeture de la connexion MongoDB...")
    if mongodb.client:
        mongodb.client.close()
    logger.info("Connexion MongoDB fermée")
