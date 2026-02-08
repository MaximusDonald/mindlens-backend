"""
Service de gestion sécurisée des fichiers uploadés
Gère l'upload, la validation et le nettoyage automatique
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime, timedelta
from fastapi import UploadFile

from app.config import settings
from app.utils.security import generate_secure_filename, get_safe_path
from app.utils.validators import validate_upload_file

logger = logging.getLogger(__name__)


class FileHandler:
    """Gestionnaire de fichiers avec nettoyage automatique"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.max_file_age = timedelta(minutes=10)  # Suppression après 10min
        
    async def save_upload(self, file: UploadFile) -> Tuple[Path, bytes, str]:
        """
        Sauvegarde temporaire d'un fichier uploadé
        
        Args:
            file: Fichier uploadé via FastAPI
            
        Returns:
            Tuple (filepath, content, detected_mime_type)
            
        Raises:
            HTTPException: Si validation échoue
        """
        # 1. Validation complète
        content, detected_mime = await validate_upload_file(file)
        
        # 2. Générer un nom sécurisé
        safe_filename = generate_secure_filename(file.filename)
        
        # 3. Construire le chemin sécurisé
        filepath = get_safe_path(self.upload_dir, safe_filename)
        
        if filepath is None:
            logger.error(f"Path traversal attempt detected: {file.filename}")
            raise ValueError("Invalid file path")
        
        # 4. Sauvegarder le fichier
        try:
            async with asyncio.Lock():  # Éviter les race conditions
                filepath.write_bytes(content)
            
            logger.info(f"File saved: {safe_filename} ({len(content)} bytes)")
            
            # 5. Programmer la suppression automatique
            asyncio.create_task(self._schedule_cleanup(filepath))
            
            return filepath, content, detected_mime
            
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            # Nettoyer si échec
            if filepath.exists():
                filepath.unlink()
            raise
    
    async def _schedule_cleanup(self, filepath: Path, delay_seconds: int = 600):
        """
        Programme la suppression automatique d'un fichier
        
        Args:
            filepath: Chemin du fichier à supprimer
            delay_seconds: Délai avant suppression (défaut: 10min)
        """
        await asyncio.sleep(delay_seconds)
        await self.delete_file(filepath)
    
    async def delete_file(self, filepath: Path) -> bool:
        """
        Supprime un fichier de manière sécurisée
        
        Args:
            filepath: Chemin du fichier
            
        Returns:
            True si supprimé, False sinon
        """
        try:
            if filepath.exists():
                filepath.unlink()
                logger.info(f"File deleted: {filepath.name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {filepath}: {e}")
            return False
    
    async def cleanup_old_files(self):
        """
        Nettoie tous les fichiers plus vieux que max_file_age
        Appelé périodiquement par un scheduler
        """
        now = datetime.now()
        deleted_count = 0
        
        try:
            for filepath in self.upload_dir.iterdir():
                if filepath.is_file() and filepath.name != ".gitkeep":
                    # Vérifier l'âge du fichier
                    file_age = now - datetime.fromtimestamp(filepath.stat().st_mtime)
                    
                    if file_age > self.max_file_age:
                        if await self.delete_file(filepath):
                            deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Cleanup: deleted {deleted_count} old file(s)")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def get_file_info(self, filepath: Path) -> Optional[dict]:
        """
        Récupère les informations d'un fichier
        
        Args:
            filepath: Chemin du fichier
            
        Returns:
            Dict avec les infos ou None
        """
        if not filepath.exists():
            return None
        
        stat = filepath.stat()
        
        return {
            "name": filepath.name,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }


# Instance globale du gestionnaire
file_handler = FileHandler()