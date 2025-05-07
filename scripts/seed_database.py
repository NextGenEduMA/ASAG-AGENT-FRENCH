"""
Script pour initialiser la base de données avec des données de test.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.models.source_text import SourceTextCreate
from app.db.repositories.text_repository import TextRepository
from app.api.dependencies import get_asag_service

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

# Données de test
SAMPLE_TEXTS = [
    {
        "title": "La forêt enchantée",
        "content": """Dans la forêt enchantée, les arbres parlent doucement entre eux. 
        Ils racontent des histoires anciennes que seuls les animaux comprennent. 
        Les écureuils sautent de branche en branche pour écouter ces récits. 
        Les oiseaux chantent pour ajouter de la musique. 
        Quand le soleil se couche, la forêt s'illumine de petites lumières magiques.""",
        "type": "récit",
        "grade": "CE1",
        "tags": ["nature", "animaux", "magie"],
        "difficulty": 2,
        "teacherId": "60d5ec9f0b4b0b3e3c7a1b3c",  # ID fictif
        "isActive": True
    },
    {
        "title": "Les saisons",
        "content": """Le printemps apporte des fleurs colorées et des oiseaux qui reviennent de leur voyage.
        L'été nous offre du soleil chaud et des journées longues pour jouer dehors.
        L'automne colore les feuilles en orange et rouge avant qu'elles ne tombent.
        L'hiver couvre tout de neige blanche et nous permet de faire des bonhommes de neige.""",
        "type": "informatif",
        "grade": "CP",
        "tags": ["saisons", "nature", "temps"],
        "difficulty": 1,
        "teacherId": "60d5ec9f0b4b0b3e3c7a1b3c",  # ID fictif
        "isActive": True
    },
    {
        "title": "La planète bleue",
        "content": """Notre planète Terre est appelée la planète bleue car vue de l'espace, les océans qui recouvrent 71% de sa surface lui donnent cette couleur dominante.
        Ces océans abritent une diversité étonnante de vie marine, des minuscules planctons aux immenses baleines bleues.
        Le cycle de l'eau permet aux océans, aux nuages et aux rivières de maintenir la vie sur Terre.
        Chaque être humain a la responsabilité de protéger cette ressource précieuse en évitant la pollution et en consommant l'eau avec sagesse.""",
        "type": "informatif",
        "grade": "CM2",
        "tags": ["planète", "eau", "environnement"],
        "difficulty": 4,
        "teacherId": "60d5ec9f0b4b0b3e3c7a1b3c",  # ID fictif
        "isActive": True
    }
]


async def seed_database():
    """Initialise la base de données avec des données de test."""
    logger.info("Début de l'initialisation de la base de données")

    # Connexion à MongoDB
    await connect_to_mongo()

    try:
        # Créer le repository de textes
        text_repo = TextRepository()

        # Obtenir le service ASAG
        asag_service = get_asag_service()

        # Ajouter les textes et générer des questions
        for text_data in SAMPLE_TEXTS:
            logger.info(f"Traitement du texte: {text_data['title']}")

            # Créer l'objet SourceTextCreate
            #text_create = SourceTextCreate(**text_data)
            text_create = SourceTextCreate(**{**text_data, "teacherId": str(text_data["teacherId"])})

            # Traiter le texte avec le service ASAG
            try:
                result = await asag_service.process_new_text(text_create, question_count=5)
                logger.info(f"Texte traité avec succès: {result['text'].title}")
                logger.info(f"Nombre de questions générées: {len(result['questions'])}")
            except Exception as e:
                logger.error(f"Erreur lors du traitement du texte: {str(e)}")

        logger.info("Initialisation de la base de données terminée avec succès")

    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
    finally:
        # Fermer la connexion MongoDB
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(seed_database())
