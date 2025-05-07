import logging
from typing import List, Dict, Any, Optional
from app.services.text_service import TextService
from app.services.question_service import QuestionService
from app.services.answer_service import AnswerService
from app.models.source_text import SourceTextCreate
from app.models.student_answer import StudentAnswerCreate
from app.models.student import Student

logger = logging.getLogger(__name__)


class ASAGService:
    """
    Service principal de l'agent ASAG qui orchestre les différents sous-services
    pour fournir les fonctionnalités complètes.
    """

    def __init__(
            self,
            text_service: TextService,
            question_service: QuestionService,
            answer_service: AnswerService
    ):
        self.text_service = text_service
        self.question_service = question_service
        self.answer_service = answer_service

    async def process_new_text(
            self,
            text_data: SourceTextCreate,
            question_count: int = 5,
            question_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Traite un nouveau texte : création, analyse et génération de questions.

        Args:
            text_data: Données du texte à créer
            question_count: Nombre de questions à générer
            question_types: Types de questions à générer

        Returns:
            Dictionnaire contenant le texte, l'analyse et les questions générées
        """
        logger.info(f"Traitement d'un nouveau texte: {text_data.title}")

        try:
            # 1. Créer le texte
            text = await self.text_service.create_text(text_data)

            # 2. Analyser le texte
            text_analysis = await self.text_service.analyze_text(str(text.id))

            # 3. Générer les questions
            generated_questions = await self.question_service.generate_questions_from_text_analysis(
                str(text.id), text_analysis, question_count, question_types
            )

            return {
                "text": text,
                "analysis": text_analysis,
                "questions": generated_questions
            }

        except Exception as e:
            logger.error(f"Erreur lors du traitement du texte: {str(e)}")
            raise

    async def evaluate_student_answer(
            self,
            answer_data: StudentAnswerCreate,
            student: Student
    ) -> Dict[str, Any]:
        """
        Évalue la réponse d'un élève et génère un feedback.

        Args:
            answer_data: Données de la réponse à évaluer
            student: Informations sur l'élève

        Returns:
            Résultat de l'évaluation avec feedback
        """
        logger.info(f"Évaluation de la réponse de l'élève ID: {answer_data.studentId}")

        try:
            # Déléguer au service de réponse
            result = await self.answer_service.submit_answer(answer_data, student)
            return result

        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation de la réponse: {str(e)}")
            raise

    async def get_questions_for_text(self, text_id: str) -> List[Dict[str, Any]]:
        """Récupère toutes les questions pour un texte source."""
        return await self.question_service.get_questions_by_text(text_id)