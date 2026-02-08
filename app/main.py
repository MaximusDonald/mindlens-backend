"""
Point d'entrée de l'application FastAPI
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import asyncio
from contextlib import asynccontextmanager

from app.config import settings, constants
from app.models.schemas import HealthCheckResponse
from app.services.file_handler import file_handler

# Configuration du logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialisation du rate limiter
limiter = Limiter(key_func=get_remote_address)


# Background tasks pour le nettoyage
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gère le cycle de vie de l'application
    Lance les tâches de fond au démarrage
    """
    # Startup
    logger.info("🚀 Starting MindLens API...")
    logger.info("📁 Starting background tasks...")
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    yield
    
    # Shutdown
    logger.info("🛑 Stopping background tasks...")
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    logger.info("👋 MindLens API stopped")


async def periodic_cleanup():
    """
    Tâche de nettoyage périodique des fichiers
    S'exécute toutes les 5 minutes
    """
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            logger.info("🧹 Running periodic file cleanup...")
            await file_handler.cleanup_old_files()
        except asyncio.CancelledError:
            logger.info("Cleanup task cancelled")
            break
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")


# Création de l'application FastAPI avec lifespan
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API d'analyse multimodale avec Gemini 3 - Transforme images et documents en raisonnement structuré",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Attacher le limiter à l'app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Exception handlers globaux
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global pour les exceptions non gérées"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Erreur interne du serveur" if not settings.DEBUG else str(exc),
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )


# Routes de base
@app.get("/", tags=["Root"])
async def root():
    """Route racine avec informations de l'API"""
    return {
        "name": "MindLens API",
        "version": settings.APP_VERSION,
        "description": "L'IA qui voit, raisonne et explique",
        "docs": "/docs" if settings.DEBUG else "Documentation désactivée en production",
        "endpoints": {
            "analyze": "/api/analyze (POST)",
            "types": "/api/analysis-types (GET)",
            "health": "/health (GET)"
        }
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """Health check endpoint global"""
    return HealthCheckResponse(
        status="ok",
        version=settings.APP_VERSION,
        gemini_configured=bool(settings.GEMINI_API_KEY)
    )


# Import et inclusion du router d'analyse
from app.routes import analysis

app.include_router(
    analysis.router,
    prefix="/api",
    tags=["Analysis"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )