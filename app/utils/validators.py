"""
Validateurs pour les fichiers uploadés
"""
import filetype
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException

from app.config import settings, constants


def validate_file_size(file_size: int) -> bool:
    """
    Valide la taille du fichier
    
    Args:
        file_size: Taille en bytes
        
    Returns:
        True si valide
    """
    return 0 < file_size <= settings.MAX_FILE_SIZE


def validate_file_extension(filename: str) -> bool:
    """
    Valide l'extension du fichier
    
    Args:
        filename: Nom du fichier
        
    Returns:
        True si extension autorisée
    """
    ext = Path(filename).suffix.lower()
    return ext in settings.get_allowed_extensions_set()


def validate_mime_type(content_type: str) -> bool:
    """
    Valide le type MIME
    
    Args:
        content_type: Type MIME du fichier
        
    Returns:
        True si type autorisé
    """
    return content_type.lower() in settings.get_allowed_mime_types_set()


def validate_file_content(file_bytes: bytes) -> Tuple[bool, str]:
    """
    Valide le contenu réel du fichier (magic bytes)
    
    Args:
        file_bytes: Contenu du fichier
        
    Returns:
        Tuple (is_valid, detected_mime_type)
    """
    # Détecter le type réel du fichier
    kind = filetype.guess(file_bytes)
    
    if kind is None:
        # Peut être du texte brut
        try:
            file_bytes.decode('utf-8')
            return True, "text/plain"
        except UnicodeDecodeError:
            return False, "unknown"
    
    detected_mime = kind.mime
    
    # Vérifier que le type détecté est autorisé
    is_valid = detected_mime in settings.get_allowed_mime_types_set()
    
    return is_valid, detected_mime


async def validate_upload_file(file: UploadFile) -> Tuple[bytes, str]:
    """
    Validation complète d'un fichier uploadé
    
    Args:
        file: Fichier uploadé via FastAPI
        
    Returns:
        Tuple (file_content, detected_mime_type)
        
    Raises:
        HTTPException: Si validation échoue
    """
    # 1. Vérifier l'extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=constants.ERROR_MESSAGES["invalid_extension"]
        )
    
    # 2. Vérifier le type MIME déclaré
    if not validate_mime_type(file.content_type):
        raise HTTPException(
            status_code=400,
            detail=constants.ERROR_MESSAGES["invalid_file_type"]
        )
    
    # 3. Lire le contenu
    content = await file.read()
    
    # 4. Vérifier la taille
    if not validate_file_size(len(content)):
        raise HTTPException(
            status_code=413,
            detail=constants.ERROR_MESSAGES["file_too_large"]
        )
    
    # 5. Vérifier le contenu réel (magic bytes)
    is_valid, detected_mime = validate_file_content(content)
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=constants.ERROR_MESSAGES["invalid_file_type"]
        )
    
    # Tout est OK, retourner le contenu et le type détecté
    return content, detected_mime