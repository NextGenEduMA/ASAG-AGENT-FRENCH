import logging
from typing import Dict, Any, Optional, List
from app.nlp.llm_client import LLMClient
from app.nlp.embeddings import EmbeddingProcessor

logger = logging.getLogger(__name__)


class SemanticMatcher:
    """
    Classe responsable de la comparaison sémantique entre
    la réponse de l'élève et le modèle de réponse attendue.
    """

    def __init__(self, llm_client: LLMClient, embedding_processor: EmbeddingProcessor):
        self.llm_client = llm_client
        self.embedding_processor = embedding_processor

    async def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité sémantique entre deux textes.

        Args:
            text1: Premier texte (généralement la réponse de l'élève)
            text2: Deuxième texte (généralement la réponse attendue)

        Returns:
            Score de similarité entre 0 et 1
        """
        try:
            # Méthode 1: Cosine similarity basée sur les embeddings
            embedding_similarity = await self.embedding_processor.compute_cosine_similarity(text1, text2)

            # Méthode 2: Évaluation par le LLM
            llm_similarity = await self._compute_llm_similarity(text1, text2)

            # Moyenne pondérée des deux approches
            # On donne un poids plus important à l'évaluation LLM qui est plus contextuelle
            final_similarity = (embedding_similarity * 0.3) + (llm_similarity * 0.7)

            logger.debug(
                f"Similarité sémantique: {final_similarity} (embedding: {embedding_similarity}, LLM: {llm_similarity})")
            return final_similarity

        except Exception as e:
            logger.error(f"Erreur lors du calcul de similarité: {str(e)}")
            # En cas d'erreur, retourner une valeur par défaut prudente
            return 0.5

    async def check_element_presence(self, text: str, element: str) -> float:
        """
        Vérifie si un élément clé est présent sémantiquement dans un texte.

        Args:
            text: Texte dans lequel chercher (réponse de l'élève)
            element: Élément à rechercher

        Returns:
            Score de présence entre 0 et 1
        """
        try:
            # Utiliser le LLM pour détecter la présence conceptuelle
            prompt = f"""
            Détermine si le concept ou l'idée suivant est présent dans le texte donné, 
            même s'il est exprimé avec des mots différents.

            Concept à rechercher: "{element}"

            Texte: "{text}"

            Indique sur une échelle de 0 à 1 à quel point ce concept est présent dans le texte.
            Réponds uniquement avec un nombre entre 0 et 1, sans explication.
            """

            response = await self.llm_client.generate_text(prompt)

            # Extraire le score
            try:
                score = float(response.strip())
                score = max(0, min(1, score))  # Limiter entre 0 et 1
                return score
            except ValueError:
                logger.warning(f"Réponse non numérique du LLM: {response}")
                return 0.5

        except Exception as e:
            logger.error(f"Erreur lors de la vérification d'élément: {str(e)}")
            return 0.5

    async def _compute_llm_similarity(self, text1: str, text2: str) -> float:
        """
        Utilise le LLM pour évaluer la similarité sémantique entre deux textes.
        """
        prompt = f"""
        Compare les deux textes suivants et évalue leur similarité sémantique 
        (c'est-à-dire la correspondance de sens, pas nécessairement des mots exacts).

        Texte 1: "{text1}"

        Texte 2: "{text2}"

        Indique sur une échelle de 0 à 1 à quel point ces textes expriment la même idée ou information.
        Réponds uniquement avec un nombre entre 0 et 1, sans explication.
        """

        response = await self.llm_client.generate_text(prompt)

        # Extraire le score
        try:
            score = float(response.strip())
            score = max(0, min(1, score))  # Limiter entre 0 et 1
            return score
        except ValueError:
            logger.warning(f"Réponse non numérique du LLM: {response}")
            return 0.5