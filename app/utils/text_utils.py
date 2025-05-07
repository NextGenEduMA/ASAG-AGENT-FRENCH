"""
Utilitaires pour le traitement de texte.
"""

import re
import unicodedata
from typing import Dict, Any


def normalize_text(text: str) -> str:
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


def check_grammar(text: str, grade: str = "CE2") -> Dict[str, Any]:
    """
    Vérifie la grammaire d'un texte selon le niveau scolaire.

    Args:
        text: Texte à vérifier
        grade: Niveau scolaire (CP, CE1, CE2, CM1, CM2)

    Returns:
        Dictionnaire avec les problèmes détectés et un score
    """
    # Pour la simplicité, cette implémentation est minimale
    # Dans une version réelle, utilisez un vérificateur grammatical complet

    issues = []
    score = 1.0  # Score parfait par défaut

    # Vérifications de base
    if not text:
        issues.append("La réponse est vide")
        score = 0.0
        return {"issues": issues, "score": score}

    # Vérifier la ponctuation finale
    if not text.strip().endswith(('.', '!', '?')):
        issues.append("La phrase devrait se terminer par un point")
        score -= 0.1

    # Vérifier la majuscule au début
    if not text.strip()[0].isupper():
        issues.append("La phrase devrait commencer par une majuscule")
        score -= 0.1

    # Vérifier les phrases trop courtes
    if len(text.split()) < 3:
        issues.append("La réponse est très courte")
        score -= 0.2

    # Limiter le score entre 0 et 1
    score = max(0, min(1, score))

    return {
        "issues": issues,
        "score": score
    }