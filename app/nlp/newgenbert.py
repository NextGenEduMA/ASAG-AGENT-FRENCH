import logging
import os
from typing import Dict, Any, List, Optional
import numpy as np
import torch
from transformers import CamembertModel, CamembertTokenizer, AutoModelForSequenceClassification, AutoTokenizer

logger = logging.getLogger(__name__)


class NewGenBERT:
    """
    Wrapper pour un modèle CamemBERT adapté à l'évaluation automatique
    des réponses courtes en français.
    """

    def __init__(self, model_path: str = None, use_gpu: bool = False):
        """
        Initialise le modèle pour l'évaluation des réponses.

        Args:
            model_path: Chemin vers le modèle pré-entraîné
            use_gpu: Utiliser le GPU si disponible
        """
        self.model_path = model_path or os.getenv("NLP_MODEL_PATH", "camembert-base")
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.device = torch.device("cuda" if self.use_gpu else "cpu")

        self.tokenizer = None
        self.model = None

        logger.info(f"Initialisation du modèle CamemBERT pour l'évaluation: {self.model_path}")
        logger.info(f"Utilisation du GPU: {self.use_gpu}")

    def load_model(self):
        """Charge le modèle et le tokenizer."""
        try:
            logger.info(f"Chargement du tokenizer: {self.model_path}")
            self.tokenizer = CamembertTokenizer.from_pretrained(self.model_path)

            logger.info(f"Chargement du modèle CamemBERT: {self.model_path}")
            self.model = CamembertModel.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()  # Passer en mode évaluation

            logger.info("Modèle chargé avec succès")

        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {str(e)}")
            raise

    async def analyze_answer(
            self,
            student_answer: str,
            reference_answer: str,
            key_elements: List[str]
    ) -> Dict[str, Any]:
        """
        Analyse une réponse d'élève par rapport à une réponse de référence.

        Args:
            student_answer: Réponse de l'élève
            reference_answer: Réponse de référence
            key_elements: Éléments clés qui devraient être présents

        Returns:
            Dictionnaire contenant les résultats de l'analyse
        """
        # Assurer que le modèle est chargé
        if self.model is None or self.tokenizer is None:
            self.load_model()

        logger.info(f"Analyse de réponse en utilisant CamemBERT")

        try:
            # Tokeniser les textes
            student_tokens = self.tokenizer(student_answer, return_tensors="pt", padding=True, truncation=True,
                                            max_length=512).to(self.device)
            reference_tokens = self.tokenizer(reference_answer, return_tensors="pt", padding=True, truncation=True,
                                              max_length=512).to(self.device)

            # Obtenir les embeddings
            with torch.no_grad():
                student_output = self.model(**student_tokens)
                reference_output = self.model(**reference_tokens)

            # Utiliser les embeddings de la couche [CLS] pour la similarité globale
            student_emb = student_output.last_hidden_state[:, 0, :].cpu().numpy()
            reference_emb = reference_output.last_hidden_state[:, 0, :].cpu().numpy()

            # Normaliser les vecteurs
            student_emb_norm = student_emb / np.linalg.norm(student_emb, axis=1, keepdims=True)
            reference_emb_norm = reference_emb / np.linalg.norm(reference_emb, axis=1, keepdims=True)

            # Calculer la similarité cosinus
            cosine_sim = np.dot(student_emb_norm, reference_emb_norm.T)
            similarity_score = float(cosine_sim[0][0])

            # Vérifier la présence des éléments clés
            key_elements_present = []
            key_elements_scores = {}

            for element in key_elements:
                # Tokeniser l'élément clé
                element_tokens = self.tokenizer(element, return_tensors="pt", padding=True, truncation=True,
                                                max_length=128).to(self.device)

                # Obtenir son embedding
                with torch.no_grad():
                    element_output = self.model(**element_tokens)

                element_emb = element_output.last_hidden_state[:, 0, :].cpu().numpy()
                element_emb_norm = element_emb / np.linalg.norm(element_emb, axis=1, keepdims=True)

                # Calculer la similarité avec la réponse de l'élève
                element_sim = np.dot(student_emb_norm, element_emb_norm.T)
                element_score = float(element_sim[0][0])

                # Sauvegarder le score
                key_elements_scores[element] = element_score

                # Considérer l'élément comme présent si la similarité est supérieure à un seuil
                # ou si l'élément est littéralement présent dans la réponse
                threshold = 0.7
                if element_score > threshold or element.lower() in student_answer.lower():
                    key_elements_present.append(element)

            # Calculer un score global
            content_score = len(key_elements_present) / len(key_elements) if key_elements else 0.5

            # Combiner les scores (70% contenu, 30% similarité globale)
            final_score = (content_score * 0.7) + (similarity_score * 0.3)

            # Déterminer un statut basé sur le score
            status = "excellent" if final_score > 0.9 else \
                "correct" if final_score > 0.75 else \
                    "acceptable" if final_score > 0.6 else \
                        "partially_correct" if final_score > 0.4 else "incorrect"

            return {
                "score": final_score,
                "content_score": content_score,
                "similarity_score": similarity_score,
                "key_elements_present": key_elements_present,
                "key_elements_missing": [e for e in key_elements if e not in key_elements_present],
                "key_elements_scores": key_elements_scores,
                "status": status
            }

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de la réponse: {str(e)}")
            raise
