import json
from contextlib import asynccontextmanager

from bson import ObjectId
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import questions, answers, texts
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection

# Classe encodeur JSON personnalisé pour gérer ObjectId
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware pour encoder les réponses JSON avec notre encodeur personnalisé
@app.middleware("http")
async def custom_json_middleware(request, call_next):
    response = await call_next(request)

    # Vérifier si la réponse est JSON
    if isinstance(response, JSONResponse):
        # Récupérer le contenu de la réponse
        content = response.body.decode()
        # Décoder en Python
        python_obj = json.loads(content)
        # Réencoder avec notre encodeur personnalisé
        new_content = json.dumps(python_obj, cls=CustomJSONEncoder)
        # Créer une nouvelle réponse
        return JSONResponse(
            content=json.loads(new_content),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    return response

# Inclusion des routeurs API
app.include_router(questions.router, prefix="/api/questions")
app.include_router(answers.router, prefix="/api/answers")
app.include_router(texts.router, prefix="/api/texts")

@app.get("/health")
async def health_check():
    return {"status": "ok"}