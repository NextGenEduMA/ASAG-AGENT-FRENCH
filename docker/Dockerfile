FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installation de Poetry
RUN pip install poetry==1.4.2

# Copie du fichier de configuration Poetry
COPY pyproject.toml ./

# Configuration de Poetry pour ne pas créer d'environnement virtuel
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copie du code source
COPY ./app ./app

# Exécution
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
