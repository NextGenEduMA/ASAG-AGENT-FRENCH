from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional

from app.models.open_question import OpenQuestion, OpenQuestionCreate, OpenQuestionUpdate
from app.models.answer_template import AnswerTemplate, AnswerTemplateCreate, AnswerTemplateUpdate
from app.services.question_service import QuestionService
from app.api.dependencies import get_question_service, get_text_service

from app.services.text_service import TextService

router = APIRouter(tags=["questions"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_question(
        question_in: OpenQuestionCreate,
        template_in: Optional[AnswerTemplateCreate] = None,
        question_service: QuestionService = Depends(get_question_service)
):
    """
    Crée une nouvelle question ouverte avec son modèle de réponse.

    Args:
        question_in: Données de la question à créer
        template_in: Données du modèle de réponse (optionnel)
    """
    result = await question_service.create_question(question_in, template_in)
    return result


@router.get("/{question_id}")
async def get_question(
        question_id: str,
        question_service: QuestionService = Depends(get_question_service)
):
    """Récupère une question avec son modèle de réponse."""
    result = await question_service.get_question_with_template(question_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question avec ID {question_id} non trouvée"
        )
    return result


@router.put("/{question_id}", response_model=OpenQuestion)
async def update_question(
        question_id: str,
        question_in: OpenQuestionUpdate,
        question_service: QuestionService = Depends(get_question_service)
):
    """Met à jour une question existante."""
    question = await question_service.update_question(question_id, question_in)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question avec ID {question_id} non trouvée"
        )
    return question


@router.put("/templates/{template_id}", response_model=AnswerTemplate)
async def update_answer_template(
        template_id: str,
        template_in: AnswerTemplateUpdate,
        question_service: QuestionService = Depends(get_question_service)
):
    """Met à jour un modèle de réponse existant."""
    template = await question_service.update_answer_template(template_id, template_in)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modèle de réponse avec ID {template_id} non trouvé"
        )
    return template


@router.get("/text/{text_id}")
async def get_questions_by_text(
        text_id: str,
        question_service: QuestionService = Depends(get_question_service)
):
    """Récupère toutes les questions pour un texte source avec leurs modèles de réponse."""
    result = await question_service.get_questions_by_text(text_id)
    return result


@router.post("/generate/{text_id}", status_code=status.HTTP_201_CREATED)
async def generate_questions(
        text_id: str,
        count: int = 5,
        question_types: Optional[List[str]] = None,
        question_service: QuestionService = Depends(get_question_service),
        text_service: TextService = Depends(get_text_service)
):
    """
    Génère des questions à partir d'un texte source.

    Args:
        text_id: ID du texte source
        count: Nombre de questions à générer
        question_types: Types de questions à générer (optionnel)
    """
    try:
        # Analyser le texte
        text_analysis = await text_service.analyze_text(text_id)

        # Générer les questions
        result = await question_service.generate_questions_from_text_analysis(
            text_id, text_analysis, count, question_types
        )

        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération des questions: {str(e)}"
        )
