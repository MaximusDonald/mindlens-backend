"""
Routes pour l'analyse de fichiers avec Gemini
"""
import logging
from typing import Literal
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse

from app.models.schemas import AnalysisResponse, ErrorResponse
from app.services.file_handler import file_handler
from app.services.gemini_service import gemini_analyzer
from app.config import constants
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

# Création du router
router = APIRouter()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Fichier invalide"},
        413: {"model": ErrorResponse, "description": "Fichier trop volumineux"},
        429: {"model": ErrorResponse, "description": "Trop de requêtes"},
        500: {"model": ErrorResponse, "description": "Erreur serveur"}
    },
    summary="Analyser un fichier avec Gemini",
    description="Upload une image ou document texte pour analyse intelligente"
)
@limiter.limit("5/minute")  # 5 requêtes par minute par IP
async def analyze_file(
    request: Request,
    file: UploadFile = File(..., description="Fichier à analyser (image ou texte)"),
    analysis_type: Literal["infrastructure", "data", "document"] = Form(
        ..., 
        description="Type d'analyse à effectuer"
    )
):
    """
    Endpoint principal d'analyse
    
    **Workflow:**
    1. Validation stricte du fichier (type, taille, contenu)
    2. Sauvegarde temporaire sécurisée
    3. Analyse avec Gemini selon le type choisi
    4. Suppression automatique du fichier
    5. Retour de l'analyse structurée
    
    **Types d'analyse:**
    - `infrastructure`: Routes, bâtiments, espaces publics
    - `data`: Graphiques, tableaux, statistiques
    - `document`: Rapports, articles, textes
    """
    filepath = None
    
    try:
        logger.info(f"Received analysis request: {file.filename}, type: {analysis_type}")
        
        # 1. Validation et sauvegarde du fichier
        filepath, content, detected_mime = await file_handler.save_upload(file)
        
        logger.info(f"File validated and saved: {filepath.name}")
        
        # 2. Déterminer le type de contenu
        is_image = detected_mime.startswith("image/")
        is_text = detected_mime in ["text/plain", "application/pdf"]
        
        # 3. Analyse avec Gemini
        if is_image:
            result = await gemini_analyzer.analyze_image(
                image_bytes=content,
                analysis_type=analysis_type,
                mime_type=detected_mime
            )
        elif is_text:
            # Décoder le texte
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                # Essayer avec d'autres encodages
                try:
                    text_content = content.decode('latin-1')
                except:
                    raise HTTPException(
                        status_code=400,
                        detail="Impossible de décoder le fichier texte"
                    )
            
            result = await gemini_analyzer.analyze_text(
                text_content=text_content,
                analysis_type=analysis_type
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Type de fichier non supporté: {detected_mime}"
            )
        
        logger.info("Analysis completed successfully")
        
        # 4. Retourner la réponse structurée
        return AnalysisResponse(**result)
        
    except HTTPException:
        # Re-lever les HTTPException sans modification
        raise
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=constants.ERROR_MESSAGES["analysis_failed"]
        )
        
    finally:
        # 5. Nettoyage : supprimer le fichier immédiatement
        if filepath and filepath.exists():
            await file_handler.delete_file(filepath)
            logger.debug(f"Cleaned up file: {filepath.name}")


@router.get(
    "/analysis-types",
    summary="Liste des types d'analyse disponibles",
    description="Retourne la liste des types d'analyse supportés avec leurs descriptions"
)
async def get_analysis_types():
    """
    Retourne les types d'analyse disponibles
    """
    return {
        "types": [
            {
                "value": "infrastructure",
                "label": "Infrastructure & Terrain",
                "description": "Routes, bâtiments, espaces publics, sécurité",
                "examples": ["Photo de route dégradée", "Bâtiment endommagé", "Espace public"]
            },
            {
                "value": "data",
                "label": "Graphiques & Données",
                "description": "Graphiques, tableaux, statistiques, tendances",
                "examples": ["Graphique climatique", "Données financières", "Statistiques"]
            },
            {
                "value": "document",
                "label": "Documents & Rapports",
                "description": "Rapports, articles, études, synthèses",
                "examples": ["Rapport PDF", "Article", "Note stratégique"]
            }
        ]
    }


@router.get(
    "/health",
    summary="Vérifier l'état du service d'analyse",
    description="Vérifie que Gemini est configuré et accessible"
)
async def analysis_health():
    """
    Health check spécifique au service d'analyse
    """
    try:
        # Tester la connexion Gemini
        is_connected = await gemini_analyzer.test_connection()
        
        return {
            "status": "healthy" if is_connected else "degraded",
            "gemini_available": is_connected,
            "max_file_size_mb": constants.MAX_FILE_SIZE_MB,
            "rate_limit": "5 requests/minute"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )