import re
from typing import Dict, List, Any
import logging
from app.nlp.llm_client import LLMClient
from app.models.source_text import SourceText

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """
    Classe responsable de l'analyse des textes sources pour identifier
    les éléments clés, les concepts, et préparer la génération de questions.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def analyze_text(self, text: SourceText) -> Dict[str, Any]:
        """
        Analyse un texte source et retourne une structure de données
        contenant les informations clés pour la génération de questions.
        """
        logger.info(f"Analyse du texte: {text.title}")

        # Structure pour stocker les résultats de l'analyse
        analysis_result = {
            "textId": text.id,
            "title": text.title,
            "grade": text.grade,
            "difficulty": text.difficulty,
            "key_concepts": [],
            "main_themes": [],
            "vocabulary": [],
            "grammar_elements": [],
            "characters": [],
            "events": [],
            "complexity_metrics": {}
        }

        # Analyser le contenu du texte
        try:
            # 1. Extraction des concepts clés via le LLM
            key_concepts = await self._extract_key_concepts(text.content, text.grade)
            analysis_result["key_concepts"] = key_concepts

            # 2. Identifier les thèmes principaux
            main_themes = await self._identify_themes(text.content, text.grade)
            analysis_result["main_themes"] = main_themes

            # 3. Extraire le vocabulaire important
            vocabulary = await self._extract_vocabulary(text.content, text.grade)
            analysis_result["vocabulary"] = vocabulary

            # 4. Identifier les éléments grammaticaux pertinents
            grammar_elements = await self._identify_grammar_elements(text.content, text.grade)
            analysis_result["grammar_elements"] = grammar_elements

            # 5. Extraire les personnages (si applicable)
            if text.type in ["récit", "dialogue", "conte"]:
                characters = await self._extract_characters(text.content)
                analysis_result["characters"] = characters

                # 6. Identifier les événements clés (pour les récits)
                events = await self._extract_events(text.content)
                analysis_result["events"] = events

            # 7. Calculer les métriques de complexité
            complexity_metrics = self._calculate_complexity_metrics(text.content, text.grade)
            analysis_result["complexity_metrics"] = complexity_metrics

            logger.info(f"Analyse du texte {text.title} terminée avec succès")
            return analysis_result

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du texte: {str(e)}")
            raise

    async def _extract_key_concepts(self, content: str, grade: str) -> List[str]:
        """Extrait les concepts clés du texte en fonction du niveau scolaire."""
        prompt = f"""
        En tant qu'enseignant de français pour le niveau {grade}, identifie les 5 concepts clés 
        les plus importants dans le texte suivant. Ces concepts doivent être adaptés au niveau 
        scolaire et servir de base pour des questions de compréhension.

        Texte:
        ---
        {content}
        ---

        Liste des concepts clés (format: liste de mots ou expressions courtes):
        """

        response = await self.llm_client.generate_text(prompt)
        concepts = [concept.strip() for concept in response.split('\n') if concept.strip()]
        return concepts[:5]  # Limiter à 5 concepts

    async def _identify_themes(self, content: str, grade: str) -> List[str]:
        """Identifie les thèmes principaux du texte."""
        prompt = f"""
        Identifie les principaux thèmes abordés dans ce texte de niveau {grade}.

        Texte:
        ---
        {content}
        ---

        Thèmes principaux (format: liste de 3-4 thèmes maximum):
        """

        response = await self.llm_client.generate_text(prompt)
        themes = [theme.strip() for theme in response.split('\n') if theme.strip()]
        return themes[:4]  # Limiter à 4 thèmes

    async def _extract_vocabulary(self, content: str, grade: str) -> List[Dict[str, str]]:
        """Extrait le vocabulaire important en fonction du niveau scolaire."""
        prompt = f"""
        Pour un élève de {grade}, identifie 8 mots importants du texte suivant.
        Pour chaque mot, donne sa définition simple adaptée au niveau.
        Format: mot - définition simple

        Texte:
        ---
        {content}
        ---

        Vocabulaire important:
        """

        response = await self.llm_client.generate_text(prompt)
        vocabulary = []

        for line in response.split('\n'):
            if '-' in line:
                parts = line.split('-', 1)
                if len(parts) == 2:
                    word = parts[0].strip()
                    definition = parts[1].strip()
                    vocabulary.append({"word": word, "definition": definition})

        return vocabulary

    async def _identify_grammar_elements(self, content: str, grade: str) -> List[Dict[str, Any]]:
        """Identifie les éléments grammaticaux pertinents en fonction du niveau."""
        # Adapter la recherche des éléments grammaticaux en fonction du niveau
        grammar_focus = {
            "CP": ["lettres", "syllabes", "mots simples"],
            "CE1": ["noms", "verbes", "adjectifs", "phrases simples"],
            "CE2": ["noms", "verbes", "adjectifs", "déterminants", "phrases"],
            "CM1": ["noms", "verbes", "adjectifs", "adverbes", "prépositions", "phrases complexes"],
            "CM2": ["noms", "verbes", "adjectifs", "adverbes", "conjonctions", "prépositions", "phrases complexes"]
        }

        focus_elements = grammar_focus.get(grade, ["noms", "verbes", "adjectifs"])

        prompt = f"""
        Pour un texte destiné à des élèves de {grade}, identifie 5 éléments grammaticaux 
        parmi les suivants: {', '.join(focus_elements)}.

        Pour chaque élément, donne un exemple tiré du texte et explique brièvement sa nature/fonction.

        Texte:
        ---
        {content}
        ---

        Éléments grammaticaux (format: type - exemple - explication):
        """

        response = await self.llm_client.generate_text(prompt)
        grammar_elements = []

        for line in response.split('\n'):
            if line.strip() and '-' in line:
                parts = line.split('-')
                if len(parts) >= 3:
                    element_type = parts[0].strip()
                    example = parts[1].strip()
                    explanation = parts[2].strip()
                    grammar_elements.append({
                        "type": element_type,
                        "example": example,
                        "explanation": explanation
                    })

        return grammar_elements

    async def _extract_characters(self, content: str) -> List[Dict[str, str]]:
        """Extrait les personnages du texte (pour les récits et dialogues)."""
        prompt = f"""
        Identifie les personnages présents dans ce texte.
        Pour chaque personnage, donne une brève description.

        Texte:
        ---
        {content}
        ---

        Personnages (format: nom - description):
        """

        response = await self.llm_client.generate_text(prompt)
        characters = []

        for line in response.split('\n'):
            if '-' in line:
                parts = line.split('-', 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    description = parts[1].strip()
                    characters.append({"name": name, "description": description})

        return characters

    async def _extract_events(self, content: str) -> List[Dict[str, str]]:
        """Extrait les événements clés du texte (pour les récits)."""
        prompt = f"""
        Identifie les 3-5 événements principaux dans ce texte, dans l'ordre chronologique.

        Texte:
        ---
        {content}
        ---

        Événements principaux (format: numéro - description brève de l'événement):
        """

        response = await self.llm_client.generate_text(prompt)
        events = []

        for line in response.split('\n'):
            if line.strip() and '-' in line:
                parts = line.split('-', 1)
                if len(parts) == 2:
                    event_num = parts[0].strip()
                    description = parts[1].strip()
                    events.append({"order": event_num, "description": description})

        return events

    def _calculate_complexity_metrics(self, content: str, grade: str) -> Dict[str, Any]:
        """Calcule différentes métriques de complexité du texte."""
        # Nombre de mots
        words = re.findall(r'\b\w+\b', content.lower())
        word_count = len(words)

        # Nombre de phrases
        sentences = re.split(r'[.!?]+', content)
        sentence_count = len([s for s in sentences if s.strip()])

        # Longueur moyenne des mots
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0

        # Longueur moyenne des phrases
        words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0

        # Calcul de la complexité adaptée au niveau scolaire
        # Plus simple pour CP, plus complexe pour CM2
        grade_complexity = {
            "CP": {"max_word_length": 5, "max_sentence_length": 6},
            "CE1": {"max_word_length": 6, "max_sentence_length": 8},
            "CE2": {"max_word_length": 7, "max_sentence_length": 10},
            "CM1": {"max_word_length": 8, "max_sentence_length": 12},
            "CM2": {"max_word_length": 9, "max_sentence_length": 15}
        }

        grade_params = grade_complexity.get(grade, {"max_word_length": 7, "max_sentence_length": 10})

        # Calculer un score de complexité (0-100)
        word_complexity = min(100, (avg_word_length / grade_params["max_word_length"]) * 100)
        sentence_complexity = min(100, (words_per_sentence / grade_params["max_sentence_length"]) * 100)

        overall_complexity = (word_complexity + sentence_complexity) / 2

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_word_length": round(avg_word_length, 2),
            "words_per_sentence": round(words_per_sentence, 2),
            "word_complexity": round(word_complexity, 2),
            "sentence_complexity": round(sentence_complexity, 2),
            "overall_complexity": round(overall_complexity, 2)
        }
