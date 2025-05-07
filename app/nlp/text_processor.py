import logging
import re
from typing import List, Dict, Any
import unicodedata

logger = logging.getLogger(__name__)


class TextProcessor:
    """
    Classe responsable du prétraitement et de l'analyse de texte.
    Fournit des fonctionnalités utiles pour le traitement du langage naturel.
    """

    def __init__(self):
        self.stop_words_fr = self._load_stopwords()
        logger.info("TextProcessor initialisé")

    def _load_stopwords(self) -> List[str]:
        """Charge une liste de mots vides français."""
        # Liste simplifiée pour l'exemple
        return [
            "le", "la", "les", "un", "une", "des", "du", "de", "et", "à", "au", "aux",
            "ce", "ces", "cette", "cet", "il", "elle", "ils", "elles", "je", "tu", "nous", "vous",
            "qui", "que", "quoi", "dont", "où", "mais", "ou", "et", "donc", "car", "ni", "pour",
            "dans", "par", "sur", "avec", "sans", "en", "est", "sont", "a", "ont", "être", "avoir"
        ]

    def normalize_text(self, text: str) -> str:
        """
        Normalise un texte (minuscules, retrait d'accents, ponctuation, etc.).

        Args:
            text: Texte à normaliser

        Returns:
            Texte normalisé
        """
        if not text:
            return ""

        # Convertir en minuscules
        text = text.lower()

        # Remplacer les caractères spéciaux et la ponctuation par des espaces
        text = re.sub(r'[^\w\s]', ' ', text)

        # Supprimer les accents
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

        # Remplacer les séquences d'espaces multiples par un seul espace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def remove_stopwords(self, text: str) -> str:
        """
        Supprime les mots vides d'un texte.

        Args:
            text: Texte dont on veut supprimer les mots vides

        Returns:
            Texte sans mots vides
        """
        if not text:
            return ""

        words = text.split()
        filtered_words = [word for word in words if word.lower() not in self.stop_words_fr]
        return ' '.join(filtered_words)

    def extract_keywords(self, text: str, count: int = 10) -> List[str]:
        """
        Extrait les mots-clés d'un texte basé sur la fréquence.

        Args:
            text: Texte dont on veut extraire les mots-clés
            count: Nombre de mots-clés à extraire

        Returns:
            Liste des mots-clés
        """
        if not text:
            return []

        # Normaliser et supprimer les mots vides
        normalized_text = self.normalize_text(text)
        filtered_text = self.remove_stopwords(normalized_text)

        # Compter la fréquence des mots
        words = filtered_text.split()
        word_freq = {}
        for word in words:
            if len(word) > 2:  # Ignorer les mots très courts
                word_freq[word] = word_freq.get(word, 0) + 1

        # Trier par fréquence
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # Retourner les N mots les plus fréquents
        return [word for word, freq in sorted_words[:count]]

    def segment_sentences(self, text: str) -> List[str]:
        """
        Segmente un texte en phrases.

        Args:
            text: Texte à segmenter

        Returns:
            Liste de phrases
        """
        if not text:
            return []

        # Segmentation simple basée sur la ponctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def check_grammar(self, text: str, grade: str = "CE2") -> Dict[str, Any]:
        """
        Vérifie la grammaire d'un texte selon le niveau scolaire.

        Args:
            text: Texte à vérifier
            grade: Niveau scolaire (CP, CE1, CE2, CM1, CM2)

        Returns:
            Dictionnaire avec les problèmes détectés et un score
        """
        # Note: Dans une implémentation réelle, ce serait remplacé
        # par un vérificateur grammatical plus sophistiqué

        issues = []
        score = 1.0  # Score parfait par défaut

        # Vérifications simples selon le niveau
        if grade in ["CP", "CE1"]:
            # Pour les plus jeunes, vérifier principalement ponctuation et majuscules
            if not text[0].isupper():
                issues.append("La première lettre doit être une majuscule")
                score -= 0.1

            if not text.strip().endswith(('.', '!', '?')):
                issues.append("La phrase doit se terminer par un point")
                score -= 0.1

        else:  # CE2, CM1, CM2
            # Vérifications plus avancées
            sentences = self.segment_sentences(text)

            # Vérifier les majuscules au début de chaque phrase
            for i, sentence in enumerate(sentences):
                if sentence and not sentence[0].isupper():
                    issues.append(f"La phrase {i + 1} doit commencer par une majuscule")
                    score -= 0.05

            # Vérifier les répétitions excessives
            words = text.lower().split()
            word_counts = {}
            for word in words:
                if word not in self.stop_words_fr and len(word) > 3:
                    word_counts[word] = word_counts.get(word, 0) + 1

            for word, count in word_counts.items():
                if count > 3:
                    issues.append(f"Le mot '{word}' est répété {count} fois")
                    score -= 0.03

            # Vérifier la longueur des phrases (trop longues ou trop courtes)
            for i, sentence in enumerate(sentences):
                if len(sentence.split()) < 3:
                    issues.append(f"La phrase {i + 1} est très courte")
                    score -= 0.02
                elif len(sentence.split()) > 20 and grade in ["CE2", "CM1"]:
                    issues.append(f"La phrase {i + 1} est très longue")
                    score -= 0.02

        # Limiter le score entre 0 et 1
        score = max(0, min(1, score))

        return {
            "issues": issues,
            "score": score
        }