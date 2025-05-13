# ASAG-Agent

## Système d'Évaluation Automatique de Réponses Courtes pour l'Éducation Primaire

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.9-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-green)
![MongoDB](https://img.shields.io/badge/MongoDB-5.0-green)

## 📚 Description

ASAG-Agent est un système intelligent d'évaluation automatique des réponses courtes destiné aux élèves du primaire (CP à CM2). Il analyse les textes éducatifs, génère automatiquement des questions adaptées au niveau scolaire, évalue les réponses des élèves et fournit un feedback personnalisé pour favoriser leur progression.

Ce système combine des techniques avancées de traitement du langage naturel (NLP) avec une approche pédagogique centrée sur l'apprenant pour offrir une solution complète d'évaluation formative.

## 🌟 Fonctionnalités principales

- **Analyse de textes éducatifs**
  - Extraction des concepts clés, thèmes principaux, vocabulaire important
  - Analyse adaptée au niveau scolaire (CP à CM2)
  - Support de différents types de textes (récits, dialogues, textes informatifs, etc.)

- **Génération automatique de questions**
  - Création de questions de types variés (compréhension, vocabulaire, grammaire, réflexion)
  - Adaptation du niveau de difficulté selon la classe
  - Génération des critères d'évaluation et modèles de réponses

- **Évaluation intelligente des réponses**
  - Analyse sémantique des réponses des élèves
  - Détection des éléments clés attendus
  - Vérification adaptative de la grammaire et l'orthographe

- **Feedback personnalisé**
  - Génération de retours constructifs adaptés au niveau de l'élève
  - Identification des points forts et axes d'amélioration
  - Adaptation du ton et du langage selon l'âge de l'élève

- **Suivi de progression**
  - Historique des réponses et évaluations
  - Profil d'apprentissage par élève
  - Statistiques pour les enseignants

## 🏗️ Architecture technique

### Stack technologique

- **Backend**: FastAPI (Python 3.9+)
- **Base de données**: MongoDB
- **Modèles NLP**: 
  - Modèles de langage de grande taille (LLM) via différents fournisseurs (Hugging Face, OpenAI, Azure)
  - Modèles d'embeddings pour la similarité sémantique
  - Support de modèles multilingues (focus sur le français)

### Structure du projet

```
asag-agent/
├── app/
│   ├── api/               # Routes et endpoints FastAPI
│   ├── core/              # Configuration et fonctions core
│   ├── db/                # Repositories et connexion MongoDB
│   ├── models/            # Modèles de données Pydantic
│   ├── modules/           # Modules fonctionnels
│   │   ├── evaluation/    # Analyse des réponses et feedback
│   │   └── generation/    # Analyse de texte et génération de questions
│   ├── nlp/               # Services d'IA et NLP
│   ├── services/          # Couche service (logique métier)
│   └── utils/             # Utilitaires
├── docker/                # Configuration Docker
└── scripts/               # Scripts utilitaires
```

## 🚀 Installation et démarrage

### Prérequis

- Python 3.9 ou supérieur
- MongoDB 5.0 ou supérieur
- Docker et Docker Compose (optionnel)

### Installation

1. **Cloner le dépôt**

```bash
git clone https://github.com/votre-organisation/asag-agent.git
cd asag-agent
```

2. **Créer un environnement virtuel**

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**

```bash
pip install poetry
poetry install
```

4. **Configuration**

Créez un fichier `.env` à la racine du projet avec les variables nécessaires:

```
# MongoDB settings
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=asag_db

# NLP Model settings
LLM_PROVIDER=huggingface  # huggingface, openai, azure
LLM_API_KEY=your_api_key
LLM_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
LLM_API_ENDPOINT=

# Embedding model
EMBEDDING_PROVIDER=huggingface
EMBEDDING_API_KEY=your_api_key
EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-large

# Security
SECRET_KEY=your-secret-key
```

### Démarrage

#### Option 1: Développement local

1. **Démarrer MongoDB**

```bash
docker-compose -f docker/docker-compose.yml up -d mongo
```

2. **Initialiser la base de données avec les données de test**

```bash
python scripts/seed_database.py
```

3. **Démarrer l'application**

```bash
uvicorn app.main:app --reload
```

#### Option 2: Avec Docker

```bash
docker-compose -f docker/docker-compose.yml up -d
```

L'API sera accessible à l'adresse: http://localhost:8000

La documentation API sera disponible à: http://localhost:8000/docs

## 🔍 API Endpoints

### Textes

- `POST /api/texts/` - Créer un nouveau texte
- `POST /api/texts/process` - Traiter un texte (création, analyse, génération de questions)
- `GET /api/texts/{text_id}` - Récupérer un texte par ID
- `PUT /api/texts/{text_id}` - Mettre à jour un texte
- `GET /api/texts/` - Récupérer tous les textes (avec filtres optionnels)
- `GET /api/texts/{text_id}/analyze` - Analyser un texte

### Questions

- `POST /api/questions/` - Créer une nouvelle question
- `GET /api/questions/{question_id}` - Récupérer une question avec son modèle de réponse
- `PUT /api/questions/{question_id}` - Mettre à jour une question
- `PUT /api/questions/templates/{template_id}` - Mettre à jour un modèle de réponse
- `GET /api/questions/text/{text_id}` - Récupérer toutes les questions pour un texte
- `POST /api/questions/generate/{text_id}` - Générer des questions pour un texte

### Réponses et Feedback

- `POST /api/answers/submit` - Soumettre une réponse d'élève
- `GET /api/answers/student/{student_id}` - Récupérer toutes les réponses d'un élève
- `GET /api/answers/question/{question_id}` - Récupérer toutes les réponses pour une question
- `GET /api/answers/{answer_id}` - Récupérer une réponse avec son feedback
- `PUT /api/answers/feedback/{feedback_id}/helpful` - Évaluer l'utilité d'un feedback

## 📋 Modèles de données

### SourceText

```python
{
    "id": "ObjectId",
    "title": "str",
    "content": "str",
    "type": "str",  # récit, dialogue, informatif, etc.
    "grade": "str",  # CP, CE1, CE2, CM1, CM2
    "tags": ["str"],
    "difficulty": "int",  # 1-5
    "teacherId": "ObjectId",
    "isActive": "bool",
    "submittedAt": "datetime"
}
```

### OpenQuestion

```python
{
    "id": "ObjectId",
    "textId": "ObjectId",
    "questionText": "str",
    "questionType": "str",  # compréhension, vocabulaire, grammaire, réflexion
    "difficultyLevel": "int",  # 1-5
    "skills": ["str"],
    "grade": "str",  # CP, CE1, CE2, CM1, CM2
    "maxScore": "int",
    "creationMethod": "str",  # auto-generated, teacher-modified
    "isActive": "bool",
    "createdAt": "datetime"
}
```

### AnswerTemplate

```python
{
    "id": "ObjectId",
    "questionId": "ObjectId",
    "modelAnswer": "str",
    "keyElements": ["str"],
    "acceptableSynonyms": ["str"],
    "scoringRubric": "dict",
    "minimumScore": "float",
    "requiresGrammarCheck": "bool"
}
```

### StudentAnswer

```python
{
    "id": "ObjectId",
    "studentId": "ObjectId",
    "questionId": "ObjectId",
    "answerText": "str",
    "submissionMethod": "str",  # text, handwriting
    "scoreObtained": "float",
    "answerStatus": "str",  # pending, correct, partially_correct, incorrect
    "attemptNumber": "int",
    "timeSpent": "int",  # en secondes
    "submittedAt": "datetime"
}
```

### Feedback

```python
{
    "id": "ObjectId",
    "answerId": "ObjectId",
    "feedbackContent": "str",
    "correctionDetails": "dict",
    "suggestedImprovements": ["str"],
    "positivePoints": ["str"],
    "feedbackType": "str",  # encouragement, corrective, explicative
    "wasHelpful": "bool",
    "generatedAt": "datetime"
}
```

## 🧠 Composants NLP

### LLMClient

Interface unifiée pour interagir avec différents modèles de langage (Hugging Face, OpenAI, Azure).

### EmbeddingProcessor

Génère des représentations vectorielles des textes pour calculer la similarité sémantique.

### TextAnalyzer

Analyse les textes éducatifs pour en extraire les concepts clés, thèmes, vocabulaire, etc.

### QuestionGenerator

Génère des questions pédagogiques adaptées au niveau scolaire.

### SemanticMatcher

Compare sémantiquement les réponses des élèves avec les modèles de réponses attendues.

### AnswerAnalyzer

Évalue les réponses des élèves en fonction des critères pédagogiques.

### FeedbackGenerator

Génère des retours personnalisés adaptés au niveau et aux besoins de l'élève.

## 🔧 Configuration avancée

### Modèles d'IA

Le système est conçu pour être flexible quant aux modèles d'IA utilisés:

- **LLM**: Il est possible d'utiliser différents modèles de Hugging Face, OpenAI ou Azure.
- **Embeddings**: Plusieurs options sont disponibles, y compris des modèles multilingues optimisés pour le français.

Modifiez les variables d'environnement dans le fichier `.env` pour configurer les modèles:

```
LLM_PROVIDER=huggingface
LLM_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-large
```

### Adaptation aux niveaux scolaires

Le système adapte automatiquement:
- La complexité des questions
- Le langage des feedbacks
- Les critères d'évaluation

en fonction du niveau scolaire (CP à CM2) spécifié pour chaque texte.