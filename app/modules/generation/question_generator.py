import random
from typing import Dict, List, Any, Optional
import logging
from app.nlp.llm_client import LLMClient
from app.models.open_question import OpenQuestionCreate
from app.models.answer_template import AnswerTemplateCreate

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """
    Classe responsable de la génération des questions ouvertes
    à partir de l'analyse d'un texte source.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def generate_questions(
            self,
            text_analysis: Dict[str, Any],
            question_count: int = 5,
            question_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Génère des questions ouvertes basées sur l'analyse d'un texte.

        Args:
            text_analysis: Résultat de l'analyse du texte
            question_count: Nombre de questions à générer
            question_types: Types de questions à générer (compréhension, vocabulaire, etc.)

        Returns:
            Liste de dictionnaires contenant les questions et leurs modèles de réponse
        """
        logger.info(f"Génération de {question_count} questions pour le texte: {text_analysis['title']}")

        if not question_types:
            # Types de questions par défaut
            question_types = ["compréhension", "vocabulaire", "grammaire"]

            # Ajuster les types de questions selon le niveau scolaire
            if text_analysis["grade"] in ["CP", "CE1"]:
                question_types = ["compréhension", "vocabulaire"]
            elif text_analysis["grade"] in ["CM1", "CM2"]:
                question_types = ["compréhension", "vocabulaire", "grammaire", "réflexion"]

        # Distribuer les questions par type
        question_distribution = self._distribute_questions(question_count, question_types)

        generated_questions = []

        try:
            # Générer des questions pour chaque type
            for q_type, count in question_distribution.items():
                if count > 0:
                    questions = await self._generate_questions_by_type(
                        text_analysis, q_type, count
                    )
                    generated_questions.extend(questions)

            logger.info(f"Génération de {len(generated_questions)} questions terminée avec succès")
            return generated_questions

        except Exception as e:
            logger.error(f"Erreur lors de la génération des questions: {str(e)}")
            raise

    def _distribute_questions(self, total_count: int, question_types: List[str]) -> Dict[str, int]:
        """Distribue le nombre de questions entre les différents types."""
        distribution = {}
        remaining = total_count

        # S'assurer qu'il y a au moins une question de chaque type
        for q_type in question_types:
            distribution[q_type] = 1
            remaining -= 1

        # Distribuer les questions restantes proportionnellement
        while remaining > 0:
            for q_type in question_types:
                if remaining > 0:
                    distribution[q_type] += 1
                    remaining -= 1
                else:
                    break

        return distribution

    async def _generate_questions_by_type(
            self,
            text_analysis: Dict[str, Any],
            question_type: str,
            count: int
    ) -> List[Dict[str, Any]]:
        """Génère des questions d'un type spécifique."""
        if question_type == "compréhension":
            return await self._generate_comprehension_questions(text_analysis, count)
        elif question_type == "vocabulaire":
            return await self._generate_vocabulary_questions(text_analysis, count)
        elif question_type == "grammaire":
            return await self._generate_grammar_questions(text_analysis, count)
        elif question_type == "réflexion":
            return await self._generate_reflection_questions(text_analysis, count)
        else:
            logger.warning(f"Type de question inconnu: {question_type}")
            return []

    async def _generate_comprehension_questions(
            self,
            text_analysis: Dict[str, Any],
            count: int
    ) -> List[Dict[str, Any]]:
        """Génère des questions de compréhension basées sur le texte."""
        grade = text_analysis["grade"]
        key_concepts = text_analysis["key_concepts"]
        themes = text_analysis["main_themes"]

        # Adapter la complexité selon le niveau
        complexity_level = {
            "CP": "très simples, réponse directement dans le texte",
            "CE1": "simples, réponse facilement identifiable dans le texte",
            "CE2": "de difficulté moyenne, certaines demandant de faire des liens",
            "CM1": "modérément complexes, demandant des déductions simples",
            "CM2": "complexes, demandant réflexion et interprétation"
        }.get(grade, "adaptées au niveau")

        # Construire le prompt
        prompt = f"""
        En tant qu'enseignant de français pour le niveau {grade}, génère {count} questions de compréhension {complexity_level} 
        sur le texte dont les thèmes principaux sont: {', '.join(themes)} et les concepts clés: {', '.join(key_concepts)}.

        Pour chaque question, fournis également:
        1. La réponse attendue
        2. Les éléments clés que doit contenir une bonne réponse
        3. Les critères d'évaluation

        Format pour chaque question:
        QUESTION: [texte de la question]
        RÉPONSE ATTENDUE: [réponse modèle complète]
        ÉLÉMENTS CLÉS: [liste des éléments clés séparés par des virgules]
        CRITÈRES: [critères d'évaluation séparés par des virgules]
        DIFFICULTÉ: [un chiffre entre 1 et 5]
        """

        response = await self.llm_client.generate_text(prompt)

        return self._parse_generated_questions(
            response,
            text_analysis["textId"],
            grade,
            "compréhension"
        )

    async def _generate_vocabulary_questions(
            self,
            text_analysis: Dict[str, Any],
            count: int
    ) -> List[Dict[str, Any]]:
        """Génère des questions de vocabulaire basées sur le texte."""
        grade = text_analysis["grade"]
        vocabulary = text_analysis["vocabulary"]

        # Construire le prompt
        prompt = f"""
        En tant qu'enseignant de français pour le niveau {grade}, génère {count} questions sur le vocabulaire 
        adapté à ce niveau. Utilise les mots et définitions suivants comme référence:

        {', '.join([f"{item['word']} ({item['definition']})" for item in vocabulary])}

        Pour chaque question, fournis également:
        1. La réponse attendue
        2. Les éléments clés que doit contenir une bonne réponse
        3. Les critères d'évaluation

        Crée des questions variées: définition de mots, synonymes, antonymes, mots de la même famille, etc.

        Format pour chaque question:
        QUESTION: [texte de la question]
        RÉPONSE ATTENDUE: [réponse modèle complète]
        ÉLÉMENTS CLÉS: [liste des éléments clés séparés par des virgules]
        CRITÈRES: [critères d'évaluation séparés par des virgules]
        DIFFICULTÉ: [un chiffre entre 1 et 5]
        """

        response = await self.llm_client.generate_text(prompt)

        return self._parse_generated_questions(
            response,
            text_analysis["textId"],
            grade,
            "vocabulaire"
        )

    async def _generate_grammar_questions(
            self,
            text_analysis: Dict[str, Any],
            count: int
    ) -> List[Dict[str, Any]]:
        """Génère des questions de grammaire basées sur le texte."""
        grade = text_analysis["grade"]
        grammar_elements = text_analysis["grammar_elements"]

        # Construire le prompt
        prompt = f"""
        En tant qu'enseignant de français pour le niveau {grade}, génère {count} questions de grammaire 
        adaptées à ce niveau. Utilise les éléments grammaticaux suivants comme référence:

        {', '.join([f"{item['type']} (ex: {item['example']})" for item in grammar_elements])}

        Pour chaque question, fournis également:
        1. La réponse attendue
        2. Les éléments clés que doit contenir une bonne réponse
        3. Les critères d'évaluation

        Adapte la complexité au niveau {grade}.

        Format pour chaque question:
        QUESTION: [texte de la question]
        RÉPONSE ATTENDUE: [réponse modèle complète]
        ÉLÉMENTS CLÉS: [liste des éléments clés séparés par des virgules]
        CRITÈRES: [critères d'évaluation séparés par des virgules]
        DIFFICULTÉ: [un chiffre entre 1 et 5]
        """

        response = await self.llm_client.generate_text(prompt)

        return self._parse_generated_questions(
            response,
            text_analysis["textId"],
            grade,
            "grammaire"
        )

    async def _generate_reflection_questions(
            self,
            text_analysis: Dict[str, Any],
            count: int
    ) -> List[Dict[str, Any]]:
        """Génère des questions de réflexion basées sur le texte."""
        grade = text_analysis["grade"]
        themes = text_analysis["main_themes"]

        # Construire le prompt
        prompt = f"""
        En tant qu'enseignant de français pour le niveau {grade}, génère {count} questions de réflexion 
        qui amènent l'élève à développer sa pensée critique sur les thèmes suivants: {', '.join(themes)}.

        Ces questions doivent encourager la réflexion personnelle et l'expression d'opinions.

        Pour chaque question, fournis également:
        1. Un exemple de réponse attendue (sachant qu'il peut y avoir plusieurs bonnes réponses)
        2. Les éléments clés que doit contenir une bonne réponse
        3. Les critères d'évaluation

        Format pour chaque question:
        QUESTION: [texte de la question]
        RÉPONSE ATTENDUE: [exemple de réponse modèle]
        ÉLÉMENTS CLÉS: [liste des éléments clés séparés par des virgules]
        CRITÈRES: [critères d'évaluation séparés par des virgules]
        DIFFICULTÉ: [un chiffre entre 1 et 5]
        """

        response = await self.llm_client.generate_text(prompt)

        return self._parse_generated_questions(
            response,
            text_analysis["textId"],
            grade,
            "réflexion"
        )

    def _parse_generated_questions(
            self,
            generated_text: str,
            text_id: str,
            grade: str,
            question_type: str
    ) -> List[Dict[str, Any]]:
        """Parse le texte généré pour extraire les questions et les réponses."""
        questions = []
        current_question = {}
        current_section = None

        for line in generated_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith('QUESTION:'):
                # Si on a déjà une question en cours, on l'ajoute à la liste
                if current_question and 'questionText' in current_question:
                    questions.append(current_question)
                    current_question = {}

                current_question['questionText'] = line[len('QUESTION:'):].strip()
                current_question['textId'] = text_id
                current_question['grade'] = grade
                current_question['questionType'] = question_type
                current_section = 'question'

            elif line.startswith('RÉPONSE ATTENDUE:'):
                current_question['modelAnswer'] = line[len('RÉPONSE ATTENDUE:'):].strip()
                current_section = 'answer'

            elif line.startswith('ÉLÉMENTS CLÉS:'):
                elements = line[len('ÉLÉMENTS CLÉS:'):].strip()
                current_question['keyElements'] = [elem.strip() for elem in elements.split(',')]
                current_section = 'elements'

            elif line.startswith('CRITÈRES:'):
                criteria = line[len('CRITÈRES:'):].strip()
                current_question['scoringRubric'] = [crit.strip() for crit in criteria.split(',')]
                current_section = 'criteria'

            elif line.startswith('DIFFICULTÉ:'):
                try:
                    difficulty = int(line[len('DIFFICULTÉ:'):].strip())
                    current_question['difficultyLevel'] = max(1, min(5, difficulty))  # Ensure between 1-5
                except ValueError:
                    current_question['difficultyLevel'] = 3  # Default
                current_section = 'difficulty'

            elif current_section:
                # Ajouter aux sections existantes
                if current_section == 'question':
                    current_question['questionText'] += ' ' + line
                elif current_section == 'answer':
                    current_question['modelAnswer'] += ' ' + line

        # Ajouter la dernière question si elle existe
        if current_question and 'questionText' in current_question:
            questions.append(current_question)

        # Préparer les objets de retour
        result = []
        for q in questions:
            # Définir les valeurs par défaut si nécessaires
            if 'keyElements' not in q:
                q['keyElements'] = []
            if 'scoringRubric' not in q:
                q['scoringRubric'] = []
            if 'difficultyLevel' not in q:
                q['difficultyLevel'] = 3
            if 'modelAnswer' not in q:
                q['modelAnswer'] = ""

            # Configurer le score maximum en fonction de la difficulté
            q['maxScore'] = q['difficultyLevel'] * 2

            # Créer le dictionnaire final
            question_data = {
                "question": OpenQuestionCreate(
                    textId=q['textId'],
                    questionText=q['questionText'],
                    questionType=q['questionType'],
                    difficultyLevel=q['difficultyLevel'],
                    skills=q.get('scoringRubric', []),
                    grade=q['grade'],
                    maxScore=q['maxScore'],
                    isActive=True
                ),
                "answerTemplate": AnswerTemplateCreate(
                    # questionId sera défini après la création de la question
                    modelAnswer=q['modelAnswer'],
                    keyElements=q['keyElements'],
                    acceptableSynonyms=[],  # À compléter ultérieurement
                    scoringRubric={
                        "keyElements": {elem: q['maxScore'] / len(q['keyElements']) if q['keyElements'] else 0 for elem
                                        in q['keyElements']},
                        "criteria": {crit: 1 for crit in q['scoringRubric']}
                    },
                    minimumScore=q['maxScore'] * 0.6,  # 60% pour valider
                    requiresGrammarCheck=q['questionType'] in ['grammaire', 'expression']
                )
            }
            result.append(question_data)

        return result