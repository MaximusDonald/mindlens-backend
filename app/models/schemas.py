"""
Schémas Pydantic pour validation des données
"""
from typing import List, Literal
from pydantic import BaseModel, Field, validator

from app.config import constants


class AnalysisRequest(BaseModel):
    """Requête d'analyse (metadata)"""
    analysis_type: Literal["infrastructure", "data", "document"] = Field(
        ...,
        description="Type d'analyse à effectuer"
    )
    
    @validator("analysis_type")
    def validate_analysis_type(cls, v):
        if v not in constants.ANALYSIS_TYPES:
            raise ValueError(f"Type d'analyse invalide. Choix: {constants.ANALYSIS_TYPES}")
        return v


class AnalysisResponse(BaseModel):
    """Réponse structurée de l'analyse"""
    observations: str = Field(..., description="Observations factuelles")
    analysis: str = Field(..., description="Analyse et implications")
    reasoning: str = Field(..., description="Chaîne de raisonnement")
    actions: List[str] = Field(..., description="Actions recommandées")
    
    class Config:
        json_schema_extra = {
            "example": {
                "observations": "Route en mauvais état avec nids-de-poule...",
                "analysis": "Risques pour la sécurité routière...",
                "reasoning": "La dégradation progressive indique...",
                "actions": [
                    "Réparation urgente des sections critiques",
                    "Signalisation temporaire des dangers",
                    "Audit structurel complet"
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Réponse d'erreur standardisée"""
    detail: str = Field(..., description="Message d'erreur")
    error_code: str = Field(default="UNKNOWN_ERROR", description="Code d'erreur")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Fichier trop volumineux (max 10MB)",
                "error_code": "FILE_TOO_LARGE"
            }
        }


class HealthCheckResponse(BaseModel):
    """Réponse du health check"""
    status: str = "ok"
    version: str = Field(..., description="Version de l'application")
    gemini_configured: bool = Field(..., description="Indique si Gemini est configuré correctement")