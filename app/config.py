"""
Configuration centralisée de l'application
Gère les variables d'environnement et les constantes
"""
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """Configuration de l'application avec validation"""
    
    # Application
    APP_NAME: str = "MindLens API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Keys
    GEMINI_API_KEY: str = Field(..., min_length=20)
    
    # Security
    MAX_FILE_SIZE: int = Field(default=10485760, ge=1024)  # 10MB min 1KB
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=5, ge=1, le=100)
    
    # File Handling
    UPLOAD_DIR: Path = Path("uploads")
    ALLOWED_EXTENSIONS: str = ".jpg,.jpeg,.png,.webp,.txt,.pdf"
    ALLOWED_MIME_TYPES: str = "image/jpeg,image/png,image/webp,text/plain,application/pdf"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @validator("UPLOAD_DIR", pre=True)
    def create_upload_dir(cls, v):
        """Crée le dossier uploads s'il n'existe pas"""
        upload_path = Path(v)
        upload_path.mkdir(parents=True, exist_ok=True)
        return upload_path
    
    @validator("ALLOWED_ORIGINS")
    def parse_origins(cls, v):
        """Parse les origines CORS"""
        return [origin.strip() for origin in v.split(",")]
    
    @validator("ALLOWED_EXTENSIONS")
    def parse_extensions(cls, v):
        """Parse les extensions autorisées"""
        return [ext.strip().lower() for ext in v.split(",")]
    
    @validator("ALLOWED_MIME_TYPES")
    def parse_mime_types(cls, v):
        """Parse les types MIME autorisés"""
        return [mime.strip().lower() for mime in v.split(",")]
    
    def get_allowed_extensions_set(self) -> set:
        """Retourne les extensions sous forme de set"""
        return set(self.ALLOWED_EXTENSIONS)
    
    def get_allowed_mime_types_set(self) -> set:
        """Retourne les types MIME sous forme de set"""
        return set(self.ALLOWED_MIME_TYPES)


# Instance globale de configuration
settings = Settings()


# Constantes dérivées (lecture seule)
class Constants:
    """Constantes de l'application"""
    
    # Tailles
    MAX_FILE_SIZE_MB = settings.MAX_FILE_SIZE / (1024 * 1024)
    
    # Types d'analyse supportés
    ANALYSIS_TYPES = ["infrastructure", "data", "document"]
    
    # Messages d'erreur standardisés
    ERROR_MESSAGES = {
        "file_too_large": f"Fichier trop volumineux (max {MAX_FILE_SIZE_MB}MB)",
        "invalid_file_type": "Type de fichier non supporté",
        "invalid_extension": "Extension de fichier non autorisée",
        "upload_failed": "Échec du téléchargement du fichier",
        "analysis_failed": "Échec de l'analyse",
        "gemini_error": "Erreur lors de l'appel à Gemini",
        "rate_limit_exceeded": "Trop de requêtes, réessayez plus tard"
    }


constants = Constants()