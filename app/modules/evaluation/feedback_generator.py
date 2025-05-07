import logging
from typing import Dict, Any, List
from app.models.student_answer import StudentAnswer
from app.models.open_question import OpenQuestion
from app.models.answer_template import AnswerTemplate
from app.models.student import Student
from app.models.feedback import FeedbackCreate
from app.nlp.llm_client import LLMClient

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    """
    Classe responsable de la génération de feedback personnalisé
    pour les réponses des élèves.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def generate_feedback(
            self,
            analysis_result: Dict[str, Any],
            student: Student,
            student_answer: StudentAnswer,
            question: OpenQuestion,
            answer_template: AnswerTemplate
    ) -> FeedbackCreate:
        """
        Génère un feedback personnalisé basé sur l'analyse de la réponse.

        Args:
            analysis_result: Résultats de l'analyse de la réponse
            student: Informations sur l'élève
            student_answer: Réponse de l'élève
            question: Question posée
            answer_template: Modèle de réponse attendue

        Returns:
            Objet FeedbackCreate contenant le feedback généré
        """
        logger.info(f"Génération de feedback pour la réponse ID: {student_answer.id}")

        # Déterminer le type de feedback en fonction du statut de la réponse
        feedback_type = self._determine_feedback_type(analysis_result["status"])

        # Préparer les éléments pour le feedback
        feedback_elements = {
            # Information générale
            "student_name": f"{student.firstName} {student.lastName}",
            "student_grade": student.grade,
            "question_text": question.questionText,
            "answer_text": student_answer.answerText,
            "model_answer": answer_template.modelAnswer,
            "score": analysis_result["raw_score"],
            "max_score": analysis_result["max_score"],
            "percentage": analysis_result["percentage_score"],
            "status": analysis_result["status"],

            # Éléments trouvés et manquants
            "key_elements_found": analysis_result["key_elements_found"],
            "key_elements_missing": analysis_result["key_elements_missing"],
            "grammar_issues": analysis_result["grammar_issues"],

            # Niveau de la réponse
            "question_type": question.questionType,
            "difficulty_level": question.difficultyLevel
        }

        # Générer le contenu du feedback
        feedback_content = await self._generate_feedback_content(
            feedback_elements,
            feedback_type,
            student.grade
        )

        # Extraire les suggestions et points positifs
        correction_details = {
            "score": analysis_result["raw_score"],
            "maxScore": analysis_result["max_score"],
            "percentage": analysis_result["percentage_score"],
            "status": analysis_result["status"],
            "keyElementsFound": analysis_result["key_elements_found"],
            "keyElementsMissing": analysis_result["key_elements_missing"],
            "grammarIssues": analysis_result["grammar_issues"]
        }

        # Extraire les suggestions et points positifs du feedback
        suggested_improvements, positive_points = await self._extract_suggestions_and_positives(
            feedback_content,
            feedback_elements
        )

        # Créer l'objet feedback
        feedback = FeedbackCreate(
            answerId=student_answer.id,
            feedbackContent=feedback_content,
            correctionDetails=correction_details,
            suggestedImprovements=suggested_improvements,
            positivePoints=positive_points,
            feedbackType=feedback_type
        )

        logger.info(f"Feedback généré avec succès pour la réponse ID: {student_answer.id}")
        return feedback

    def _determine_feedback_type(self, status: str) -> str:
        """Détermine le type de feedback en fonction du statut de la réponse."""
        if status in ["excellent", "correct"]:
            return "encouragement"
        elif status == "acceptable":
            return "nuancé"
        elif status == "partially_correct":
            return "correctif"
        else:  # incorrect
            return "explicatif"

    async def _generate_feedback_content(
            self,
            elements: Dict[str, Any],
            feedback_type: str,
            grade: str
    ) -> str:
        """
        Génère le contenu textuel du feedback en utilisant le LLM.
        """
        # Adaptation du ton et du langage selon le niveau scolaire
        language_level = {
            "CP": "très simple avec des mots courts et des phrases courtes",
            "CE1": "simple avec des phrases courtes",
            "CE2": "accessible avec un vocabulaire de base",
            "CM1": "clair et direct avec un vocabulaire varié",
            "CM2": "riche mais toujours accessible, avec un style encourageant"
        }.get(grade, "adapté à l'âge")

        # Construction du prompt en fonction du type de feedback
        if feedback_type == "encouragement":
            prompt = f"""
            Génère un feedback positif et encourageant pour un élève de {grade} 
            qui a bien répondu à une question. Le langage doit être {language_level}.

            Question: {elements['question_text']}

            Réponse de l'élève: {elements['answer_text']}

            Points forts: 
            - L'élève a inclus les éléments clés suivants: {', '.join(elements['key_elements_found']) if elements['key_elements_found'] else 'aucun'}
            - Score obtenu: {elements['score']}/{elements['max_score']} ({elements['percentage']:.1f}%)

            Le feedback doit:
            1. Féliciter l'élève spécifiquement pour les bons éléments de sa réponse
            2. Souligner un ou deux points particulièrement bien faits
            3. Suggérer une petite amélioration possible (même pour une excellente réponse)
            4. Se terminer par un encouragement positif

            Utilise un ton chaleureux et enthousiaste adapté à un élève de {grade}.
            """

        elif feedback_type == "nuancé":
            prompt = f"""
            Génère un feedback constructif pour un élève de {grade} 
            qui a partiellement bien répondu à une question. Le langage doit être {language_level}.

            Question: {elements['question_text']}

            Réponse de l'élève: {elements['answer_text']}

            Réponse attendue: {elements['model_answer']}

            Points forts: 
            - L'élève a inclus les éléments clés suivants: {', '.join(elements['key_elements_found']) if elements['key_elements_found'] else 'aucun'}

            Points à améliorer:
            - Éléments manquants: {', '.join(elements['key_elements_missing']) if elements['key_elements_missing'] else 'aucun'}
            - Problèmes de grammaire: {', '.join(elements['grammar_issues']) if elements['grammar_issues'] else 'aucun'}

            Score obtenu: {elements['score']}/{elements['max_score']} ({elements['percentage']:.1f}%)

            Le feedback doit:
            1. Commencer par un point positif spécifique sur ce que l'élève a bien fait
            2. Expliquer simplement ce qui pourrait être amélioré, en donnant 1-2 exemples concrets
            3. Suggérer comment l'élève pourrait compléter sa réponse
            4. Se terminer par un encouragement

            Utilise un ton positif mais informatif, adapté à un élève de {grade}.
            """

        elif feedback_type == "correctif":
            prompt = f"""
            Génère un feedback correctif mais bienveillant pour un élève de {grade} 
            qui a partiellement répondu à une question avec des lacunes importantes. Le langage doit être {language_level}.

            Question: {elements['question_text']}

            Réponse de l'élève: {elements['answer_text']}

            Réponse attendue: {elements['model_answer']}

            Points forts: 
            - L'élève a inclus les éléments clés suivants: {', '.join(elements['key_elements_found']) if elements['key_elements_found'] else 'aucun'}

            Points à améliorer:
            - Éléments manquants: {', '.join(elements['key_elements_missing']) if elements['key_elements_missing'] else 'aucun'}
            - Problèmes de grammaire: {', '.join(elements['grammar_issues']) if elements['grammar_issues'] else 'aucun'}

            Score obtenu: {elements['score']}/{elements['max_score']} ({elements['percentage']:.1f}%)

            Le feedback doit:
            1. Commencer par reconnaître au moins un aspect positif de la réponse, même s'il est mineur
            2. Expliquer clairement ce qui n'est pas complet ou correct
            3. Montrer un exemple de meilleure réponse pour 1-2 points spécifiques
            4. Donner des conseils précis sur comment mieux répondre à ce type de question
            5. Se terminer par un encouragement à persévérer

            Utilise un ton bienveillant et constructif, sans être décourageant, adapté à un élève de {grade}.
            """

        else:  # explicatif - pour les réponses incorrectes
            prompt = f"""
            Génère un feedback explicatif et pédagogique pour un élève de {grade} 
            qui n'a pas correctement répondu à une question. Le langage doit être {language_level}.

            Question: {elements['question_text']}

            Réponse de l'élève: {elements['answer_text']}

            Réponse attendue: {elements['model_answer']}

            Points à améliorer:
            - Éléments manquants: {', '.join(elements['key_elements_missing']) if elements['key_elements_missing'] else 'aucun'}
            - Problèmes de grammaire: {', '.join(elements['grammar_issues']) if elements['grammar_issues'] else 'aucun'}

            Score obtenu: {elements['score']}/{elements['max_score']} ({elements['percentage']:.1f}%)

            Le feedback doit:
            1. Commencer par une phrase encourageante pour l'effort fourni
            2. Expliquer simplement pourquoi la réponse n'est pas correcte
            3. Présenter clairement les éléments qui auraient dû figurer dans la réponse
            4. Donner un exemple concret de bonne réponse, adapté au niveau
            5. Suggérer une méthode ou une stratégie pour mieux comprendre ce type de question
            6. Se terminer par un encouragement à réessayer

            Utilise un ton pédagogique et patient, sans être condescendant, adapté à un élève de {grade}.
            """

        # Générer le feedback avec le LLM
        try:
            feedback_content = await self.llm_client.generate_text(prompt)
            return feedback_content
        except Exception as e:
            logger.error(f"Erreur lors de la génération du feedback: {str(e)}")
            return f"Bravo pour ton effort ! Tu as obtenu {elements['score']}/{elements['max_score']} points. Continue à t'améliorer !"

    async def _extract_suggestions_and_positives(
            self,
            feedback_content: str,
            elements: Dict[str, Any]
    ) -> tuple[List[str], List[str]]:
        """
        Extrait les suggestions d'amélioration et les points positifs du feedback généré.
        """
        # Utiliser le LLM pour extraire ces éléments
        prompt = f"""
        Analyse le feedback suivant destiné à un élève et extrais:
        1. Les suggestions d'amélioration (maximum 3)
        2. Les points positifs mentionnés (maximum 3)

        Format de réponse:
        SUGGESTIONS:
        - suggestion 1
        - suggestion 2
        - suggestion 3

        POINTS POSITIFS:
        - point positif 1
        - point positif 2
        - point positif 3

        Feedback à analyser:
        {feedback_content}
        """

        try:
            response = await self.llm_client.generate_text(prompt)

            suggestions = []
            positives = []
            current_section = None

            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue

                if line == "SUGGESTIONS:":
                    current_section = "suggestions"
                elif line == "POINTS POSITIFS:":
                    current_section = "positives"
                elif line.startswith("- ") and current_section:
                    item = line[2:].strip()
                    if current_section == "suggestions":
                        suggestions.append(item)
                    else:
                        positives.append(item)

            # Si rien n'a été extrait, utiliser des valeurs par défaut
            if not suggestions:
                if elements["key_elements_missing"]:
                    suggestions.append(
                        f"Ajouter les éléments manquants: {', '.join(elements['key_elements_missing'][:2])}")
                else:
                    suggestions.append("Développer ta réponse davantage")

            if not positives:
                if elements["key_elements_found"]:
                    positives.append(f"Tu as bien mentionné: {', '.join(elements['key_elements_found'][:2])}")
                else:
                    positives.append("Tu as fait l'effort de répondre à la question")

            return suggestions, positives

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des suggestions: {str(e)}")

            # Valeurs par défaut en cas d'erreur
            default_suggestions = ["Relire attentivement la question", "Ajouter plus de détails dans ta réponse"]
            default_positives = ["Tu as fait l'effort de répondre à la question"]

            return default_suggestions, default_positives