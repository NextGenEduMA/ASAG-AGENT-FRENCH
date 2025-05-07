import logging
import os
import numpy as np
from typing import List, Dict, Any, Optional
import aiohttp
import torch
from transformers import AutoModel, AutoTokenizer

logger = logging.getLogger(__name__)


class EmbeddingProcessor:
    """
    Classe pour gérer les embeddings (représentations vectorielles) de textes.
    Ces embeddings sont utilisés pour calculer la similarité sémantique.
    """

    def __init__(self):
        self.api_key = os.getenv("EMBEDDING_API_KEY", "")
        self.model_name = os.getenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-large")
        self.provider = os.getenv("EMBEDDING_PROVIDER", "huggingface")

        # Initialiser le modèle local si nécessaire
        self.local_model = None
        self.local_tokenizer = None

        if self.provider == "local":
            self._init_local_model()
        elif self.provider == "openai":
            self.endpoint = "https://api.openai.com/v1/embeddings"
        elif self.provider == "huggingface":
            self.endpoint = f"https://api-inference.huggingface.co/models/{self.model_name}"

        logger.info(f"Embedding Processor initialisé avec le modèle {self.model_name}")

    def _init_local_model(self):
        """Initialise le modèle local pour les embeddings."""
        try:
            # Charger le modèle et le tokenizer de Hugging Face
            logger.info(f"Chargement du modèle d'embedding local: {self.model_name}")
            self.local_tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.local_model = AutoModel.from_pretrained(self.model_name)

            # Passer en mode évaluation et sur GPU si disponible
            self.local_model.eval()
            if torch.cuda.is_available():
                self.local_model = self.local_model.to("cuda")
                logger.info("Modèle d'embedding déplacé sur GPU")

            logger.info("Modèle d'embedding local chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle d'embedding local: {str(e)}")
            raise

    async def get_embedding(self, text: str) -> List[float]:
        """
        Obtient l'embedding (vecteur) d'un texte.

        Args:
            text: Texte à transformer en vecteur

        Returns:
            Vecteur d'embedding (liste de floats)
        """
        logger.debug(f"Obtention d'embedding pour: {text[:30]}...")

        # Sélectionner la méthode appropriée selon le fournisseur
        if self.provider == "openai":
            return await self._get_embedding_openai(text)
        elif self.provider == "huggingface":
            return await self._get_embedding_huggingface(text)
        elif self.provider == "local":
            return self._get_embedding_local(text)
        else:
            raise ValueError(f"Fournisseur d'embedding non supporté: {self.provider}")

    async def compute_cosine_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité cosinus entre deux textes.

        Args:
            text1: Premier texte
            text2: Deuxième texte

        Returns:
            Score de similarité entre 0 (aucune similarité) et 1 (identiques)
        """
        try:
            # Obtenir les embeddings pour les deux textes
            embedding1 = await self.get_embedding(text1)
            embedding2 = await self.get_embedding(text2)

            # Convertir en arrays numpy
            vector1 = np.array(embedding1)
            vector2 = np.array(embedding2)

            # Normaliser les vecteurs
            vector1 = vector1 / np.linalg.norm(vector1)
            vector2 = vector2 / np.linalg.norm(vector2)

            # Calculer la similarité cosinus
            cosine_similarity = np.dot(vector1, vector2)

            # Normaliser à [0, 1]
            similarity = (cosine_similarity + 1) / 2

            logger.debug(f"Similarité calculée: {similarity}")
            return float(similarity)

        except Exception as e:
            logger.error(f"Erreur lors du calcul de similarité: {str(e)}")
            raise

    async def _get_embedding_openai(self, text: str) -> List[float]:
        """Obtient l'embedding en utilisant l'API OpenAI."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model_name,
            "input": text
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_msg = await response.text()
                        logger.error(f"Erreur OpenAI Embedding: {error_msg}")
                        raise Exception(f"Erreur API OpenAI Embedding: {response.status} - {error_msg}")

                    result = await response.json()
                    return result["data"][0]["embedding"]

        except Exception as e:
            logger.error(f"Erreur lors de l'obtention d'embedding OpenAI: {str(e)}")
            raise

    async def _get_embedding_huggingface(self, text: str) -> List[float]:
        """Obtient l'embedding en utilisant l'API Hugging Face."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "inputs": text,
            "options": {"wait_for_model": True}
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_msg = await response.text()
                        logger.error(f"Erreur Hugging Face Embedding: {error_msg}")
                        raise Exception(f"Erreur API Hugging Face Embedding: {response.status} - {error_msg}")

                    result = await response.json()
                    # Le format peut varier selon le modèle Hugging Face
                    if isinstance(result, list):
                        return result[0]
                    return result["embeddings"]

        except Exception as e:
            logger.error(f"Erreur lors de l'obtention d'embedding Hugging Face: {str(e)}")
            raise

    def _get_embedding_local(self, text: str) -> List[float]:
        """
        Génère un embedding en utilisant un modèle local.

        Args:
            text: Texte à transformer en vecteur

        Returns:
            Vecteur d'embedding (liste de floats)
        """
        try:
            # S'assurer que le modèle est chargé
            if self.local_model is None or self.local_tokenizer is None:
                self._init_local_model()

            # Prétraiter le texte
            inputs = self.local_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

            # Déplacer sur GPU si disponible
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}

            # Obtenir l'embedding
            with torch.no_grad():
                outputs = self.local_model(**inputs)

            # Pour la plupart des modèles, utiliser la sortie [CLS]
            embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]

            return embedding.tolist()

        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embedding local: {str(e)}")
            raise