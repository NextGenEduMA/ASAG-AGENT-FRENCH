from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import questions, answers, texts
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code d'initialisation
    await connect_to_mongo()
    yield
    # Code de nettoyage
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API pour l'agent ASAG (Automatic Short Answer Grading)",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
"""app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)"""

# Inclusion des routeurs API
app.include_router(questions.router, prefix="/api/questions")
app.include_router(answers.router, prefix="/api/answers")
app.include_router(texts.router, prefix="/api/texts")

@app.get("/health")
async def health_check():
    return {"status": "ok"}