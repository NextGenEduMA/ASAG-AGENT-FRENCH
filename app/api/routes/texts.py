from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional

from app.models.source_text import SourceText, SourceTextCreate, SourceTextUpdate
from app.services.text_service import TextService
from app.services.asag_service import ASAGService
from app.api.dependencies import get_text_service, get_asag_service

router = APIRouter(tags=["texts"])


@router.post("/", response_model=SourceText, status_code=status.HTTP_201_CREATED)
async def create_text(
        text_in: SourceTextCreate,
        text_service: TextService = Depends(get_text_service)
):
    """Crée un nouveau texte source."""
    return await text_service.create_text(text_in)


@router.post("/process", status_code=status.HTTP_201_CREATED)
async def process_text(
        text_in: SourceTextCreate,
        question_count: int = 5,
        question_types: Optional[List[str]] = None,
        asag_service: ASAGService = Depends(get_asag_service)
):
    """
    Traite un nouveau texte : création, analyse et génération de questions.

    Args:
        text_in: Données du texte à créer
        question_count: Nombre de questions à générer
        question_types: Types de questions à générer (optionnel)
    """
    result = await asag_service.process_new_text(text_in, question_count, question_types)
    return result


@router.get("/{text_id}", response_model=SourceText)
async def get_text(
        text_id: str,
        text_service: TextService = Depends(get_text_service)
):
    """Récupère un texte source par son ID."""
    text = await text_service.get_text(text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Texte avec ID {text_id} non trouvé"
        )
    return text


@router.put("/{text_id}", response_model=SourceText)
async def update_text(
        text_id: str,
        text_in: SourceTextUpdate,
        text_service: TextService = Depends(get_text_service)
):
    """Met à jour un texte source existant."""
    text = await text_service.update_text(text_id, text_in)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Texte avec ID {text_id} non trouvé"
        )
    return text


@router.get("/", response_model=List[SourceText])
async def get_all_texts(
        teacher_id: Optional[str] = None,
        grade: Optional[str] = None,
        text_service: TextService = Depends(get_text_service)
):
    """
    Récupère tous les textes sources avec filtres optionnels.

    Args:
        teacher_id: Filtrer par enseignant (optionnel)
        grade: Filtrer par niveau scolaire (optionnel)
    """
    if teacher_id:
        return await text_service.get_texts_by_teacher(teacher_id)
    elif grade:
        return await text_service.get_texts_by_grade(grade)
    else:
        return await text_service.get_all_texts()


@router.get("/{text_id}/analyze", response_model=Dict[str, Any])
async def analyze_text(
        text_id: str,
        text_service: TextService = Depends(get_text_service)
):
    """Analyse un texte source pour extraction des éléments clés."""
    try:
        result = await text_service.analyze_text(text_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'analyse du texte: {str(e)}"
        )
