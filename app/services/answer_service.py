import logging
from typing import List, Optional, Dict, Any
from app.db.repositories.student_answer_repository import StudentAnswerRepository
from app.db.repositories.feedback_repository import FeedbackRepository
from app.db.repositories.question_repository import QuestionRepository
from app.db.repositories.answer_template_repository import AnswerTemplateRepository
from app.models.student_answer import StudentAnswer, StudentAnswerCreate, StudentAnswerUpdate
from app.models.feedback import Feedback, FeedbackCreate, FeedbackUpdate
from app.modules.evaluation.answer_analyzer import AnswerAnalyzer
from app.modules.evaluation.feedback_generator import FeedbackGenerator
from app.models.student import Student

logger = logging.getLogger(__name__)


class AnswerService:
    """Service pour la gestion des réponses des élèves et des feedbacks."""

    def __init__(
            self,
            student_answer_repository: StudentAnswerRepository,
            feedback_repository: FeedbackRepository,
            question_repository: QuestionRepository,
            answer_template_repository: AnswerTemplateRepository,
            answer_analyzer: AnswerAnalyzer,
            feedback_generator: FeedbackGenerator
    ):
        self.student_answer_repository = student_answer_repository
        self.feedback_repository = feedback_repository
        self.question_repository = question_repository
        self.answer_template_repository = answer_template_repository
        self.answer_analyzer = answer_analyzer
        self.feedback_generator = feedback_generator

    async def submit_answer(self, answer_in: StudentAnswerCreate, student: Student) -> Dict[str, Any]:
        """
        Soumet une réponse d'élève, l'analyse et génère un feedback.

        Args:
            answer_in: Données de la réponse à soumettre
            student: Informations sur l'élève

        Returns:
            Dictionnaire contenant la réponse, l'analyse et le feedback
        """
        logger.info(
            f"Soumission d'une réponse de l'élève ID: {answer_in.studentId} pour la question ID: {answer_in.questionId}")

        try:
            # 1. Récupérer le nombre de tentatives précédentes
            previous_attempts = await self.student_answer_repository.get_by_student_and_question(
                str(answer_in.studentId), str(answer_in.questionId)
            )

            # Mettre à jour le numéro de tentative
            answer_data = answer_in.dict()
            answer_data["attemptNumber"] = len(previous_attempts) + 1

            # 2. Créer la réponse
            student_answer = await self.student_answer_repository.create_answer(
                StudentAnswerCreate(**answer_data)
            )

            # 3. Récupérer la question et son modèle de réponse
            question = await self.question_repository.get(str(answer_in.questionId))
            if not question:
                raise ValueError(f"Question avec ID {answer_in.questionId} non trouvée")

            templates = await self.answer_template_repository.get_by_question(str(answer_in.questionId))
            if not templates:
                raise ValueError(f"Modèle de réponse pour la question ID {answer_in.questionId} non trouvé")

            answer_template = templates[0]

            # 4. Analyser la réponse
            analysis_result = await self.answer_analyzer.analyze_answer(
                student_answer, question, answer_template
            )

            # 5. Mettre à jour le score et le statut de la réponse
            await self.student_answer_repository.update_answer(
                str(student_answer.id),
                StudentAnswerUpdate(
                    scoreObtained=analysis_result["raw_score"],
                    answerStatus=analysis_result["status"]
                )
            )

            # Mettre à jour l'objet student_answer avec les nouvelles valeurs
            student_answer.scoreObtained = analysis_result["raw_score"]
            student_answer.answerStatus = analysis_result["status"]

            # 6. Générer un feedback
            feedback = await self.feedback_generator.generate_feedback(
                analysis_result, student, student_answer, question, answer_template
            )

            # 7. Enregistrer le feedback
            created_feedback = await self.feedback_repository.create_feedback(feedback)

            return {
                "answer": student_answer,
                "analysis": analysis_result,
                "feedback": created_feedback
            }

        except Exception as e:
            logger.error(f"Erreur lors de la soumission de la réponse: {str(e)}")
            raise

    async def get_student_answers(self, student_id: str) -> List[StudentAnswer]:
        """Récupère toutes les réponses d'un élève."""
        return await self.student_answer_repository.get_by_student(student_id)

    async def get_question_answers(self, question_id: str) -> List[StudentAnswer]:
        """Récupère toutes les réponses pour une question spécifique."""
        return await self.student_answer_repository.get_by_question(question_id)

    async def get_answer_with_feedback(self, answer_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une réponse avec son feedback."""
        answer = await self.student_answer_repository.get(answer_id)
        if not answer:
            return None

        feedbacks = await self.feedback_repository.get_by_answer(answer_id)
        latest_feedback = feedbacks[0] if feedbacks else None

        return {
            "answer": answer,
            "feedback": latest_feedback
        }

    async def update_feedback_helpfulness(
            self,
            feedback_id: str,
            was_helpful: bool
    ) -> Optional[Feedback]:
        """Met à jour l'utilité d'un feedback (évalué par l'élève)."""
        return await self.feedback_repository.update_feedback(
            feedback_id,
            FeedbackUpdate(wasHelpful=was_helpful)
        )
