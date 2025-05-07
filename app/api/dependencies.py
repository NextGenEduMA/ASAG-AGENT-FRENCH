from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from app.services.text_service import TextService
from app.services.question_service import QuestionService
from app.services.answer_service import AnswerService
from app.services.asag_service import ASAGService
from app.db.repositories.text_repository import TextRepository
from app.db.repositories.question_repository import QuestionRepository
from app.db.repositories.answer_template_repository import AnswerTemplateRepository
from app.db.repositories.student_answer_repository import StudentAnswerRepository
from app.db.repositories.feedback_repository import FeedbackRepository
from app.modules.generation.text_analyzer import TextAnalyzer
from app.modules.generation.question_generator import QuestionGenerator
from app.modules.evaluation.answer_analyzer import AnswerAnalyzer
from app.modules.evaluation.semantic_matcher import SemanticMatcher
from app.modules.evaluation.feedback_generator import FeedbackGenerator
from app.nlp.llm_client import LLMClient
from app.nlp.embeddings import EmbeddingProcessor
from app.models.student import Student

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dépendances pour les repositories
def get_text_repository() -> TextRepository:
    return TextRepository()


def get_question_repository() -> QuestionRepository:
    return QuestionRepository()


def get_answer_template_repository() -> AnswerTemplateRepository:
    return AnswerTemplateRepository()


def get_student_answer_repository() -> StudentAnswerRepository:
    return StudentAnswerRepository()


def get_feedback_repository() -> FeedbackRepository:
    return FeedbackRepository()


# Dépendances pour les modules NLP
def get_llm_client() -> LLMClient:
    return LLMClient()


def get_embedding_processor() -> EmbeddingProcessor:
    return EmbeddingProcessor()


# Dépendances pour les modules de génération
def get_text_analyzer(
        llm_client: LLMClient = Depends(get_llm_client)
) -> TextAnalyzer:
    return TextAnalyzer(llm_client)


def get_question_generator(
        llm_client: LLMClient = Depends(get_llm_client)
) -> QuestionGenerator:
    return QuestionGenerator(llm_client)


# Dépendances pour les modules d'évaluation
def get_semantic_matcher(
        llm_client: LLMClient = Depends(get_llm_client),
        embedding_processor: EmbeddingProcessor = Depends(get_embedding_processor)
) -> SemanticMatcher:
    return SemanticMatcher(llm_client, embedding_processor)


def get_answer_analyzer(
        semantic_matcher: SemanticMatcher = Depends(get_semantic_matcher)
) -> AnswerAnalyzer:
    return AnswerAnalyzer(semantic_matcher)


def get_feedback_generator(
        llm_client: LLMClient = Depends(get_llm_client)
) -> FeedbackGenerator:
    return FeedbackGenerator(llm_client)


# Dépendances pour les services
def get_text_service(
        text_repository: TextRepository = Depends(get_text_repository),
        text_analyzer: TextAnalyzer = Depends(get_text_analyzer)
) -> TextService:
    return TextService(text_repository, text_analyzer)


def get_question_service(
        question_repository: QuestionRepository = Depends(get_question_repository),
        answer_template_repository: AnswerTemplateRepository = Depends(get_answer_template_repository),
        question_generator: QuestionGenerator = Depends(get_question_generator)
) -> QuestionService:
    return QuestionService(question_repository, answer_template_repository, question_generator)


def get_answer_service(
        student_answer_repository: StudentAnswerRepository = Depends(get_student_answer_repository),
        feedback_repository: FeedbackRepository = Depends(get_feedback_repository),
        question_repository: QuestionRepository = Depends(get_question_repository),
        answer_template_repository: AnswerTemplateRepository = Depends(get_answer_template_repository),
        answer_analyzer: AnswerAnalyzer = Depends(get_answer_analyzer),
        feedback_generator: FeedbackGenerator = Depends(get_feedback_generator)
) -> AnswerService:
    return AnswerService(
        student_answer_repository,
        feedback_repository,
        question_repository,
        answer_template_repository,
        answer_analyzer,
        feedback_generator
    )


def get_asag_service(
        text_service: TextService = Depends(get_text_service),
        question_service: QuestionService = Depends(get_question_service),
        answer_service: AnswerService = Depends(get_answer_service)
) -> ASAGService:
    return ASAGService(text_service, question_service, answer_service)


# Dépendance pour récupérer l'élève connecté
async def get_current_student(
        token: str = Depends(oauth2_scheme)
) -> Student:
    # Cette fonction simule l'authentification
    # Dans une application réelle, elle vérifierait le token et récupérerait l'élève
    # depuis la base de données

    # Simulation pour l'exemple
    student = Student(
        id="60d5ec9f0b4b0b3e3c7a1b3d",
        firstName="Marie",
        lastName="Dupont",
        age=9,
        grade="CE2",
        profileAvatar="avatar1.png",
        progressLevel=0.6,
        learningProfile={"strengths": ["vocabulaire"], "weaknesses": ["grammaire"]}
    )

    return student