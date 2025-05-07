import logging
from typing import List, Optional, Dict, Any
from app.db.repositories.question_repository import QuestionRepository
from app.db.repositories.answer_template_repository import AnswerTemplateRepository
from app.models.open_question import OpenQuestion, OpenQuestionCreate, OpenQuestionUpdate
from app.models.answer_template import AnswerTemplate, AnswerTemplateCreate, AnswerTemplateUpdate
from app.modules.generation.question_generator import QuestionGenerator

logger = logging.getLogger(__name__)


class QuestionService:
    """Service pour la gestion des questions ouvertes."""

    def __init__(
            self,
            question_repository: QuestionRepository,
            answer_template_repository: AnswerTemplateRepository,
            question_generator: QuestionGenerator
    ):
        self.question_repository = question_repository
        self.answer_template_repository = answer_template_repository
        self.question_generator = question_generator

    async def create_question(
            self,
            question_in: OpenQuestionCreate,
            template_in: Optional[AnswerTemplateCreate] = None
    ) -> Dict[str, Any]:
        """
        Crée une nouvelle question ouverte avec son modèle de réponse.

        Args:
            question_in: Données de la question à créer
            template_in: Données du modèle de réponse (optionnel)

        Returns:
            Dictionnaire contenant la question et son modèle de réponse
        """
        logger.info(f"Création d'une nouvelle question")

        # Créer la question
        question = await self.question_repository.create_question(question_in)

        # Créer le modèle de réponse associé si fourni
        if template_in:
            # Associer l'ID de la question au modèle
            template_in_dict = template_in.dict()
            template_in_dict["questionId"] = question.id
            template = await self.answer_template_repository.create_template(
                AnswerTemplateCreate(**template_in_dict)
            )
        else:
            # Créer un modèle de réponse vide par défaut
            template = await self.answer_template_repository.create_template(
                AnswerTemplateCreate(
                    questionId=question.id,
                    modelAnswer="",
                    keyElements=[],
                    acceptableSynonyms=[],
                    scoringRubric={},
                    minimumScore=question.maxScore * 0.6
                )
            )

        return {
            "question": question,
            "answerTemplate": template
        }

    async def update_question(
            self,
            question_id: str,
            question_in: OpenQuestionUpdate
    ) -> Optional[OpenQuestion]:
        """Met à jour une question existante."""
        logger.info(f"Mise à jour de la question ID: {question_id}")
        return await self.question_repository.update_question(question_id, question_in)

    async def update_answer_template(
            self,
            template_id: str,
            template_in: AnswerTemplateUpdate
    ) -> Optional[AnswerTemplate]:
        """Met à jour un modèle de réponse existant."""
        logger.info(f"Mise à jour du modèle de réponse ID: {template_id}")
        return await self.answer_template_repository.update_template(template_id, template_in)

    async def get_question(self, question_id: str) -> Optional[OpenQuestion]:
        """Récupère une question par son ID."""
        return await self.question_repository.get(question_id)

    async def get_answer_template(self, template_id: str) -> Optional[AnswerTemplate]:
        """Récupère un modèle de réponse par son ID."""
        return await self.answer_template_repository.get(template_id)

    async def get_question_with_template(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une question avec son modèle de réponse."""
        question = await self.question_repository.get(question_id)
        if not question:
            return None

        templates = await self.answer_template_repository.get_by_question(str(question.id))
        template = templates[0] if templates else None

        return {
            "question": question,
            "answerTemplate": template
        }

    async def get_questions_by_text(self, text_id: str) -> List[Dict[str, Any]]:
        """Récupère toutes les questions pour un texte source avec leurs modèles de réponse."""
        questions = await self.question_repository.get_by_text(text_id)
        result = []

        for question in questions:
            templates = await self.answer_template_repository.get_by_question(str(question.id))
            template = templates[0] if templates else None

            result.append({
                "question": question,
                "answerTemplate": template
            })

        return result

    async def generate_questions_from_text_analysis(
            self,
            text_id: str,
            text_analysis: Dict[str, Any],
            count: int = 5,
            question_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Génère des questions à partir de l'analyse d'un texte.

        Args:
            text_id: ID du texte source
            text_analysis: Résultat de l'analyse du texte
            count: Nombre de questions à générer
            question_types: Types de questions à générer

        Returns:
            Liste de questions générées avec leurs modèles de réponse
        """
        logger.info(f"Génération de {count} questions pour le texte ID: {text_id}")

        # Générer les questions avec le module de génération
        generated_questions = await self.question_generator.generate_questions(
            text_analysis, count, question_types
        )

        # Créer les questions et les modèles de réponse dans la base de données
        created_questions = []

        for q_data in generated_questions:
            # S'assurer que l'ID du texte est correctement configuré
            question_data = q_data["question"].dict()
            question_data["textId"] = text_id

            # Créer la question et son modèle de réponse
            created = await self.create_question(
                OpenQuestionCreate(**question_data),
                q_data["answerTemplate"]
            )

            created_questions.append(created)

        logger.info(f"{len(created_questions)} questions créées avec succès")
        return created_questions
