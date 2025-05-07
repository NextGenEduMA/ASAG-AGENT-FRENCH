from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional

from app.models.student_answer import StudentAnswer, StudentAnswerCreate, StudentAnswerUpdate
from app.models.student import Student
from app.models.feedback import Feedback, FeedbackUpdate
from app.services.answer_service import AnswerService
from app.api.dependencies import get_answer_service, get_current_student

router = APIRouter(tags=["answers"])


@router.post("/submit", status_code=status.HTTP_201_CREATED)
async def submit_answer(
        answer_in: StudentAnswerCreate,
        student: Student = Depends(get_current_student),
        answer_service: AnswerService = Depends(get_answer_service)
):
    """
    Soumet une réponse d'élève, l'analyse et génère un feedback.

    Args:
        answer_in: Données de la réponse à soumettre
    """
    try:
        result = await answer_service.submit_answer(answer_in, student)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la soumission de la réponse: {str(e)}"
        )


@router.get("/student/{student_id}", response_model=List[StudentAnswer])
async def get_student_answers(
        student_id: str,
        answer_service: AnswerService = Depends(get_answer_service)
):
    """Récupère toutes les réponses d'un élève."""
    return await answer_service.get_student_answers(student_id)


@router.get("/question/{question_id}", response_model=List[StudentAnswer])
async def get_question_answers(
        question_id: str,
        answer_service: AnswerService = Depends(get_answer_service)
):
    """Récupère toutes les réponses pour une question spécifique."""
    return await answer_service.get_question_answers(question_id)


@router.get("/{answer_id}")
async def get_answer_with_feedback(
        answer_id: str,
        answer_service: AnswerService = Depends(get_answer_service)
):
    """Récupère une réponse avec son feedback."""
    result = await answer_service.get_answer_with_feedback(answer_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Réponse avec ID {answer_id} non trouvée"
        )
    return result


@router.put("/feedback/{feedback_id}/helpful")
async def update_feedback_helpfulness(
        feedback_id: str,
        was_helpful: bool,
        answer_service: AnswerService = Depends(get_answer_service)
):
    """Met à jour l'utilité d'un feedback (évalué par l'élève)."""
    feedback = await answer_service.update_feedback_helpfulness(feedback_id, was_helpful)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback avec ID {feedback_id} non trouvé"
        )
    return feedback