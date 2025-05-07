import logging
from typing import Dict, Any, List, Optional
from app.models.student_answer import StudentAnswer
from app.models.open_question import OpenQuestion
from app.models.answer_template import AnswerTemplate
from app.modules.evaluation.semantic_matcher import SemanticMatcher
from app.utils.text_utils import check_grammar, normalize_text

logger = logging.getLogger(__name__)


class AnswerAnalyzer:
    """
    Classe responsable de l'analyse des réponses des élèves
    en les comparant avec les modèles de réponses attendues.
    """

    def __init__(self, semantic_matcher: SemanticMatcher):
        self.semantic_matcher = semantic_matcher

    async def analyze_answer(
            self,
            student_answer: StudentAnswer,
            question: OpenQuestion,
            answer_template: AnswerTemplate
    ) -> Dict[str, Any]:
        """
        Analyse une réponse d'élève par rapport à la question et au modèle de réponse.

        Args:
            student_answer: La réponse soumise par l'élève
            question: La question associée
            answer_template: Le modèle de réponse attendue

        Returns:
            Dictionnaire contenant les résultats de l'analyse
        """
        logger.info(f"Analyse de réponse pour la question ID: {question.id}")

        # Résultat d'analyse
        analysis_result = {
            "answerId": student_answer.id,
            "questionId": question.id,
            "raw_score": 0.0,
            "max_score": question.maxScore,
            "percentage_score": 0.0,
            "status": "incorrect",
            "key_elements_found": [],
            "key_elements_missing": [],
            "grammar_issues": [],
            "analysis_details": {}
        }

        try:
            # 1. Vérification de la présence des éléments clés
            key_elements_results = await self._check_key_elements(
                student_answer.answerText,
                answer_template.keyElements,
                answer_template.acceptableSynonyms
            )

            analysis_result["key_elements_found"] = key_elements_results["found"]
            analysis_result["key_elements_missing"] = key_elements_results["missing"]
            analysis_result["analysis_details"]["key_elements_score"] = key_elements_results["score"]

            # 2. Vérification de la grammaire et de l'orthographe si nécessaire
            if answer_template.requiresGrammarCheck:
                grammar_results = check_grammar(student_answer.answerText, question.grade)
                analysis_result["grammar_issues"] = grammar_results["issues"]
                analysis_result["analysis_details"]["grammar_score"] = grammar_results["score"]
            else:
                analysis_result["analysis_details"]["grammar_score"] = 1.0  # Score parfait si non vérifié

            # 3. Calcul du score global
            raw_score = self._calculate_score(
                key_elements_results["score"],
                analysis_result["analysis_details"].get("grammar_score", 1.0),
                answer_template.scoringRubric
            )

            # Ajuster le score en fonction du maximum possible
            analysis_result["raw_score"] = min(raw_score, question.maxScore)
            analysis_result["percentage_score"] = (analysis_result["raw_score"] / question.maxScore) * 100

            # 4. Déterminer le statut de la réponse
            analysis_result["status"] = self._determine_status(
                analysis_result["raw_score"],
                answer_template.minimumScore,
                question.maxScore
            )

            # 5. Comparaison sémantique avec le modèle de réponse
            semantic_similarity = await self.semantic_matcher.compute_similarity(
                student_answer.answerText,
                answer_template.modelAnswer
            )
            analysis_result["analysis_details"]["semantic_similarity"] = semantic_similarity

            logger.info(f"Analyse terminée avec succès. Score: {analysis_result['raw_score']}/{question.maxScore}")
            return analysis_result

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de la réponse: {str(e)}")
            raise

    async def _check_key_elements(
            self,
            answer_text: str,
            key_elements: List[str],
            acceptable_synonyms: List[str]
    ) -> Dict[str, Any]:
        """
        Vérifie la présence des éléments clés dans la réponse de l'élève.

        Returns:
            Dictionnaire avec les éléments trouvés, manquants et le score
        """
        if not key_elements:
            return {"found": [], "missing": [], "score": 1.0}

        found_elements = []
        missing_elements = []

        # Normaliser le texte de la réponse
        normalized_answer = normalize_text(answer_text)

        for element in key_elements:
            element_found = False

            # Vérifier l'élément directement
            if normalize_text(element) in normalized_answer:
                element_found = True
            else:
                # Vérifier via la similitude sémantique
                similarity = await self.semantic_matcher.check_element_presence(
                    answer_text, element
                )

                if similarity >= 0.8:  # Seuil de similarité sémantique
                    element_found = True

            if element_found:
                found_elements.append(element)
            else:
                missing_elements.append(element)

        # Calculer le score basé sur la proportion d'éléments trouvés
        if len(key_elements) > 0:
            score = len(found_elements) / len(key_elements)
        else:
            score = 1.0

        return {
            "found": found_elements,
            "missing": missing_elements,
            "score": score
        }

    def _calculate_score(
            self,
            key_elements_score: float,
            grammar_score: float,
            scoring_rubric: Dict[str, Any]
    ) -> float:
        """
        Calcule le score global en fonction des différents critères.

        Le score est pondéré selon:
        - Présence des éléments clés: 70%
        - Correction grammaticale: 30%

        Ces pondérations peuvent être ajustées via le scoring_rubric.
        """
        # Pondération par défaut
        weights = {
            "key_elements": 0.7,
            "grammar": 0.3
        }

        # Ajuster les pondérations si spécifiées dans la rubrique
        if "weights" in scoring_rubric:
            weights = scoring_rubric["weights"]

        # Calculer le score pondéré
        weighted_score = (
                key_elements_score * weights["key_elements"] +
                grammar_score * weights["grammar"]
        )

        # Appliquer un facteur multiplicatif global si présent
        if "score_multiplier" in scoring_rubric:
            weighted_score *= scoring_rubric["score_multiplier"]

        return weighted_score

    def _determine_status(
            self,
            score: float,
            minimum_score: float,
            max_score: float
    ) -> str:
        """
        Détermine le statut de la réponse en fonction du score obtenu.
        """
        if score >= minimum_score:
            if score >= max_score * 0.9:  # 90% ou plus
                return "excellent"
            elif score >= max_score * 0.75:  # Entre 75% et 90%
                return "correct"
            else:  # Entre min_score et 75%
                return "acceptable"
        else:
            if score >= minimum_score * 0.6:  # Proche du minimum
                return "partially_correct"
            else:
                return "incorrect"