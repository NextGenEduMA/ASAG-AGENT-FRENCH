import logging
from typing import List, Optional, Dict, Any
from bson import ObjectId

from app.db.repositories.student_repository import StudentRepository
from app.models.student import Student, StudentCreate, StudentUpdate
from app.models.student_answer import StudentAnswer

logger = logging.getLogger(__name__)


class StudentService:
    """Service pour la gestion des élèves."""

    def __init__(self, student_repository: StudentRepository):
        self.student_repository = student_repository

    async def create_student(self, student_in: StudentCreate) -> Student:
        """Crée un nouvel élève."""
        logger.info(f"Création d'un nouvel élève: {student_in.firstName} {student_in.lastName}")
        return await self.student_repository.create_student(student_in)

    async def update_student(self, student_id: str, student_in: StudentUpdate) -> Optional[Student]:
        """Met à jour un élève existant."""
        logger.info(f"Mise à jour de l'élève ID: {student_id}")
        return await self.student_repository.update_student(student_id, student_in)

    async def get_student(self, student_id: str) -> Optional[Student]:
        """Récupère un élève par son ID."""
        return await self.student_repository.get(student_id)

    async def get_all_students(self) -> List[Student]:
        """Récupère tous les élèves."""
        return await self.student_repository.get_all()

    async def get_students_by_grade(self, grade: str) -> List[Student]:
        """Récupère tous les élèves d'un niveau scolaire spécifique."""
        return await self.student_repository.get_by_grade(grade)

    async def delete_student(self, student_id: str) -> bool:
        """Supprime un élève."""
        logger.info(f"Suppression de l'élève ID: {student_id}")
        return await self.student_repository.delete(student_id)

    async def update_progress_level(self, student_id: str, new_progress: float) -> Optional[Student]:
        """Met à jour le niveau de progression d'un élève."""
        logger.info(f"Mise à jour du niveau de progression de l'élève ID: {student_id} à {new_progress}")
        update_data = {"progressLevel": max(0.0, min(1.0, new_progress))}  # Limiter entre 0 et 1
        return await self.student_repository.update_student(student_id, StudentUpdate(**update_data))

    async def update_learning_profile(self, student_id: str, learning_profile: Dict[str, Any]) -> Optional[Student]:
        """Met à jour le profil d'apprentissage d'un élève."""
        logger.info(f"Mise à jour du profil d'apprentissage de l'élève ID: {student_id}")
        update_data = {"learningProfile": learning_profile}
        return await self.student_repository.update_student(student_id, StudentUpdate(**update_data))

    async def get_student_profile(self, student_id: str) -> Dict[str, Any]:
        """
        Récupère le profil complet d'un élève incluant ses statistiques d'apprentissage.

        Args:
            student_id: ID de l'élève

        Returns:
            Dictionnaire contenant le profil complet de l'élève
        """
        student = await self.student_repository.get(student_id)
        if not student:
            return None

        # Convertir l'élève en dictionnaire
        student_dict = student.dict()

        # Récupérer les statistiques supplémentaires (à implémenter selon vos besoins)
        # Exemple : nombre total de questions répondues, taux de réussite, etc.
        student_stats = await self._get_student_statistics(student_id)

        # Fusionner les informations
        student_dict.update(student_stats)

        return student_dict

    async def _get_student_statistics(self, student_id: str) -> Dict[str, Any]:
        """
        Calcule les statistiques d'apprentissage d'un élève.

        À implémenter en fonction de vos besoins spécifiques.
        Vous pourriez intégrer d'autres repositories comme StudentAnswerRepository
        pour récupérer l'historique des réponses, etc.
        """
        # Exemple de statistiques de base
        return {
            "statistics": {
                "totalAnswers": 0,  # À remplir avec les données réelles
                "correctAnswers": 0,
                "successRate": 0.0,
                "averageScore": 0.0,
                "topStrengths": [],
                "areasToImprove": []
            },
            "recentActivity": {
                "lastAnswerDate": None,
                "recentQuestionTopics": []
            }
        }