"""
Script pour initialiser la base de données avec des données de test.
"""

import asyncio
import logging
import sys
from pathlib import Path

from bson import ObjectId

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.models.source_text import SourceTextCreate
from app.db.repositories.text_repository import TextRepository
from app.models.teacher import TeacherCreate
from app.models.student import StudentCreate
from app.db.repositories.teacher_repository import TeacherRepository
from app.db.repositories.student_repository import StudentRepository

# Génère un nouvel ObjectId
teacher_id1 = ObjectId()
teacher_id2 = ObjectId()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

# Données de test - Textes
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
        "teacherId": teacher_id1,
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
        "teacherId": teacher_id1,
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
        "teacherId": teacher_id2,
        "isActive": True
    }
]

# Données de test - Enseignants
SAMPLE_TEACHERS = [
    {
        "firstName": "Sophie",
        "lastName": "Martin",
        "email": "sophie.martin@education.ma",
        "password": "motdepasse123",
        "profilePicture": None,
        "school": "École Primaire Hassan II"
    },
    {
        "firstName": "Mohammed",
        "lastName": "Alaoui",
        "email": "m.alaoui@education.ma",
        "password": "motdepasse456",
        "profilePicture": None,
        "school": "École Primaire Al Fath"
    }
]

# Données de test - Élèves
SAMPLE_STUDENTS = [
    {
        "firstName": "Yasmine",
        "lastName": "Benali",
        "age": 8,
        "grade": "CE2",
        "profileAvatar": "avatar_girl1.png",
        "progressLevel": 0.3,
        "learningProfile": {
            "strengths": ["vocabulaire", "compréhension"],
            "weaknesses": ["grammaire"]
        }
    },
    {
        "firstName": "Omar",
        "lastName": "Kadiri",
        "age": 7,
        "grade": "CE1",
        "profileAvatar": "avatar_boy1.png",
        "progressLevel": 0.5,
        "learningProfile": {
            "strengths": ["grammaire"],
            "weaknesses": ["vocabulaire"]
        }
    },
    {
        "firstName": "Amal",
        "lastName": "Tahiri",
        "age": 10,
        "grade": "CM2",
        "profileAvatar": "avatar_girl2.png",
        "progressLevel": 0.7,
        "learningProfile": {
            "strengths": ["expression écrite", "compréhension"],
            "weaknesses": ["orthographe"]
        }
    }
]


async def seed_database():
    """Initialise la base de données avec des données de test."""
    logger.info("Début de l'initialisation de la base de données")

    # Connexion à MongoDB
    await connect_to_mongo()

    try:
        # Création des enseignants
        teacher_repo = TeacherRepository()
        created_teachers = []

        logger.info("Création des enseignants")
        for i, teacher_data in enumerate(SAMPLE_TEACHERS):
            try:
                teacher_create = TeacherCreate(**teacher_data)
                teacher = await teacher_repo.create_teacher(teacher_create)
                created_teachers.append(teacher)
                logger.info(f"Enseignant créé: {teacher.firstName} {teacher.lastName}")

                # Remplacer l'ID de l'enseignant dans les textes
                teacher_id = teacher.id
                if i == 0:
                    # Pour le premier enseignant, mettre à jour les textes associés à teacher_id1
                    for text in SAMPLE_TEXTS:
                        if text["teacherId"] == teacher_id1:
                            text["teacherId"] = teacher_id
                else:
                    # Pour le deuxième enseignant, mettre à jour les textes associés à teacher_id2
                    for text in SAMPLE_TEXTS:
                        if text["teacherId"] == teacher_id2:
                            text["teacherId"] = teacher_id

            except Exception as e:
                logger.error(f"Erreur lors de la création de l'enseignant: {str(e)}")

        # Création des élèves
        student_repo = StudentRepository()
        created_students = []

        logger.info("Création des élèves")
        for student_data in SAMPLE_STUDENTS:
            try:
                student_create = StudentCreate(**student_data)
                student = await student_repo.create_student(student_create)
                created_students.append(student)
                logger.info(f"Élève créé: {student.firstName} {student.lastName}")
            except Exception as e:
                logger.error(f"Erreur lors de la création de l'élève: {str(e)}")

        # Créer le repository de textes et service ASAG
        text_repo = TextRepository()

        # Importer ici pour éviter les erreurs circulaires
        from app.nlp.llm_client import LLMClient
        from app.modules.generation.text_analyzer import TextAnalyzer
        from app.services.text_service import TextService
        from app.modules.generation.question_generator import QuestionGenerator
        from app.services.question_service import QuestionService
        from app.db.repositories.question_repository import QuestionRepository
        from app.db.repositories.answer_template_repository import AnswerTemplateRepository
        from app.services.answer_service import AnswerService
        from app.services.asag_service import ASAGService
        from app.db.repositories.student_answer_repository import StudentAnswerRepository
        from app.db.repositories.feedback_repository import FeedbackRepository
        from app.nlp.embeddings import EmbeddingProcessor
        from app.modules.evaluation.semantic_matcher import SemanticMatcher
        from app.modules.evaluation.answer_analyzer import AnswerAnalyzer
        from app.modules.evaluation.feedback_generator import FeedbackGenerator

        # Créer les instances nécessaires
        llm_client = LLMClient()
        text_analyzer = TextAnalyzer(llm_client)
        text_service = TextService(text_repo, text_analyzer)

        question_repo = QuestionRepository()
        answer_template_repo = AnswerTemplateRepository()
        question_generator = QuestionGenerator(llm_client)
        question_service = QuestionService(question_repo, answer_template_repo, question_generator)

        embedding_processor = EmbeddingProcessor()
        semantic_matcher = SemanticMatcher(llm_client, embedding_processor)
        answer_analyzer = AnswerAnalyzer(semantic_matcher)
        feedback_generator = FeedbackGenerator(llm_client)

        student_answer_repo = StudentAnswerRepository()
        feedback_repo = FeedbackRepository()

        answer_service = AnswerService(
            student_answer_repo,
            feedback_repo,
            question_repo,
            answer_template_repo,
            answer_analyzer,
            feedback_generator
        )

        asag_service = ASAGService(text_service, question_service, answer_service)

        # Ajouter les textes et générer des questions
        for text_data in SAMPLE_TEXTS:
            logger.info(f"Traitement du texte: {text_data['title']}")

            # Créer l'objet SourceTextCreate
            text_create = SourceTextCreate(**text_data)

            # Traiter le texte avec le service ASAG
            try:
                result = await asag_service.process_new_text(text_create, question_count=5)
                logger.info(f"Texte traité avec succès: {result['text'].title}")
                if 'questions' in result:
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