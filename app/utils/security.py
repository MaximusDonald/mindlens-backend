"""
Utilitaires de sécurité pour la gestion des fichiers
"""
import secrets
from pathlib import Path
from typing import Optional


def generate_secure_filename(original_filename: str) -> str:
    """
    Génère un nom de fichier sécurisé et unique
    
    Args:
        original_filename: Nom original du fichier
        
    Returns:
        Nom de fichier sécurisé avec extension préservée
        
    Example:
        "mon document.pdf" -> "x7k9m2p5q8r1t4w6.pdf"
    """
    # Extraire l'extension
    extension = Path(original_filename).suffix.lower()
    
    # Générer un nom aléatoire sécurisé (22 caractères)
    random_name = secrets.token_urlsafe(16)
    
    return f"{random_name}{extension}"


def sanitize_error_message(error: Exception, debug: bool = False) -> str:
    """
    Sanitize les messages d'erreur pour éviter la fuite d'informations
    
    Args:
        error: Exception capturée
        debug: Si True, retourne le message complet
        
    Returns:
        Message d'erreur sanitizé
    """
    if debug:
        return str(error)
    
    # En production, retourner un message générique
    return "Une erreur s'est produite lors du traitement"


def get_safe_path(base_dir: Path, filename: str) -> Optional[Path]:
    """
    Vérifie qu'un chemin ne sort pas du répertoire de base (path traversal)
    
    Args:
        base_dir: Répertoire de base autorisé
        filename: Nom du fichier
        
    Returns:
        Chemin sécurisé ou None si invalide
    """
    try:
        # Résoudre le chemin complet
        full_path = (base_dir / filename).resolve()
        
        # Vérifier qu'on reste dans base_dir
        if not str(full_path).startswith(str(base_dir.resolve())):
            return None
            
        return full_path
    except (ValueError, OSError):
        return None