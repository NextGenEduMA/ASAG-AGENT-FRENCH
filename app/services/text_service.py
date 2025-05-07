import logging
from typing import List, Optional, Dict, Any
from app.db.repositories.text_repository import TextRepository
from app.models.source_text import SourceText, SourceTextCreate, SourceTextUpdate
from app.modules.generation.text_analyzer import TextAnalyzer

logger = logging.getLogger(__name__)


class TextService:
    """Service pour la gestion des textes sources."""

    def __init__(self, text_repository: TextRepository, text_analyzer: TextAnalyzer):
        self.text_repository = text_repository
        self.text_analyzer = text_analyzer

    async def create_text(self, text_in: SourceTextCreate) -> SourceText:
        """Crée un nouveau texte source."""
        logger.info(f"Création d'un nouveau texte: {text_in.title}")
        return await self.text_repository.create_text(text_in)

    async def update_text(self, text_id: str, text_in: SourceTextUpdate) -> Optional[SourceText]:
        """Met à jour un texte source existant."""
        logger.info(f"Mise à jour du texte ID: {text_id}")
        return await self.text_repository.update_text(text_id, text_in)

    async def get_text(self, text_id: str) -> Optional[SourceText]:
        """Récupère un texte par son ID."""
        return await self.text_repository.get(text_id)

    async def get_all_texts(self) -> List[SourceText]:
        """Récupère tous les textes sources."""
        return await self.text_repository.get_all()

    async def get_texts_by_teacher(self, teacher_id: str) -> List[SourceText]:
        """Récupère tous les textes soumis par un enseignant spécifique."""
        return await self.text_repository.get_by_teacher(teacher_id)

    async def get_texts_by_grade(self, grade: str) -> List[SourceText]:
        """Récupère tous les textes pour un niveau scolaire spécifique."""
        return await self.text_repository.get_by_grade(grade)

    async def analyze_text(self, text_id: str) -> Dict[str, Any]:
        """Analyse un texte source pour extraction des éléments clés."""
        logger.info(f"Analyse du texte ID: {text_id}")

        text = await self.text_repository.get(text_id)
        if not text:
            raise ValueError(f"Texte avec ID {text_id} non trouvé")

        return await self.text_analyzer.analyze_text(text)