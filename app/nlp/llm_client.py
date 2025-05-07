import logging
import os
import aiohttp
import json
from typing import Dict, Any, Optional, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Client pour interagir avec le modèle de langage (LLM).
    Supporte différents modèles (Hugging Face, OpenAI, etc.)
    """

    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model_name = os.getenv("LLM_MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.2")
        self.provider = os.getenv("LLM_PROVIDER", "huggingface")

        # Configuration des endpoints selon le fournisseur
        if self.provider == "openai":
            self.endpoint = os.getenv("LLM_API_ENDPOINT", "https://api.openai.com/v1/chat/completions")
        elif self.provider == "huggingface":
            self.endpoint = f"https://api-inference.huggingface.co/models/{self.model_name}"
        elif self.provider == "azure":
            self.endpoint = os.getenv("LLM_API_ENDPOINT")
            self.deployment_name = os.getenv("LLM_DEPLOYMENT_NAME", "gpt-4")

        logger.info(f"LLM Client initialisé avec le modèle {self.model_name} et le fournisseur {self.provider}")

    async def generate_text(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Génère du texte à partir d'un prompt en utilisant le LLM configuré.

        Args:
            prompt: Le texte d'entrée pour le modèle
            max_tokens: Nombre maximum de tokens dans la réponse
            temperature: Degré de créativité (0.0 à 1.0)

        Returns:
            Texte généré par le modèle
        """
        logger.debug(f"Génération de texte avec prompt: {prompt[:50]}...")

        # Sélectionner la méthode appropriée selon le fournisseur
        if self.provider == "openai":
            return await self._generate_with_openai(prompt, max_tokens, temperature)
        elif self.provider == "huggingface":
            return await self._generate_with_huggingface(prompt, max_tokens, temperature)
        elif self.provider == "azure":
            return await self._generate_with_azure(prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Fournisseur LLM non supporté: {self.provider}")

    async def _generate_with_openai(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Génère du texte en utilisant l'API OpenAI."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Utiliser le format de messages pour les modèles chat
        if "gpt" in self.model_name.lower():
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        else:
            # Format pour les modèles Completion (ex: text-davinci-003)
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_msg = await response.text()
                        logger.error(f"Erreur OpenAI: {error_msg}")
                        raise Exception(f"Erreur API OpenAI: {response.status} - {error_msg}")

                    result = await response.json()

                    # Extraire le texte selon le format de réponse
                    if "gpt" in self.model_name.lower():
                        return result["choices"][0]["message"]["content"].strip()
                    else:
                        return result["choices"][0]["text"].strip()

        except Exception as e:
            logger.error(f"Erreur lors de la génération OpenAI: {str(e)}")
            raise

    async def _generate_with_huggingface(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Génère du texte en utilisant l'API Hugging Face Inference."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Adapter le payload selon le type de modèle
        # Pour les modèles de type "text-generation"
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False,
                "do_sample": True
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_msg = await response.text()
                        logger.error(f"Erreur Hugging Face: {error_msg}")
                        raise Exception(f"Erreur API Hugging Face: {response.status} - {error_msg}")

                    result = await response.json()

                    # Le format de réponse peut varier selon le modèle
                    if isinstance(result, list) and len(result) > 0:
                        return result[0]["generated_text"].strip()
                    return result["generated_text"].strip()

        except Exception as e:
            logger.error(f"Erreur lors de la génération Hugging Face: {str(e)}")
            raise

    async def _generate_with_azure(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Génère du texte en utilisant l'API Azure OpenAI."""
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

        # Format pour Azure OpenAI
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        # Construire l'URL avec le nom de déploiement
        endpoint_url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version=2023-05-15"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint_url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_msg = await response.text()
                        logger.error(f"Erreur Azure OpenAI: {error_msg}")
                        raise Exception(f"Erreur API Azure OpenAI: {response.status} - {error_msg}")

                    result = await response.json()
                    return result["choices"][0]["message"]["content"].strip()

        except Exception as e:
            logger.error(f"Erreur lors de la génération Azure OpenAI: {str(e)}")
            raise
