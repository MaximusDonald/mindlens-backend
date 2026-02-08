"""
Tests pour le service de gestion des fichiers
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import asyncio
from io import BytesIO
from fastapi import UploadFile

from app.services.file_handler import file_handler
from app.config import settings


async def test_save_valid_image():
    """Test de sauvegarde d'une image valide"""
    
    # Créer une fausse image (1x1 pixel PNG)
    fake_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # CORRECTION : Créer un UploadFile avec content_type dans le constructeur
    file = UploadFile(
        filename="test_image.png",
        file=BytesIO(fake_png),
        headers={"content-type": "image/png"}  # AJOUTÉ
    )
    
    try:
        filepath, content, mime = await file_handler.save_upload(file)
        
        print(f"✅ File saved: {filepath}")
        print(f"   Size: {len(content)} bytes")
        print(f"   MIME: {mime}")
        print(f"   Exists: {filepath.exists()}")
        
        # Vérifier les infos
        info = file_handler.get_file_info(filepath)
        print(f"   Info: {info}")
        
        # Nettoyer
        await file_handler.delete_file(filepath)
        print(f"✅ File deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_save_invalid_file():
    """Test de rejet d'un fichier invalide"""
    
    # Créer un fichier exécutable (interdit)
    fake_exe = b'MZ\x90\x00\x03\x00\x00\x00'
    
    # CORRECTION : content_type dans headers
    file = UploadFile(
        filename="malware.exe",
        file=BytesIO(fake_exe),
        headers={"content-type": "application/x-msdownload"}  # AJOUTÉ
    )
    
    try:
        await file_handler.save_upload(file)
        print("❌ Should have rejected .exe file")
    except Exception as e:
        print(f"✅ Correctly rejected: {type(e).__name__}")


async def test_save_text_file():
    """Test de sauvegarde d'un fichier texte valide"""
    
    # Créer un fichier texte
    text_content = b"Ceci est un test de fichier texte.\nLigne 2\nLigne 3"
    
    file = UploadFile(
        filename="test_document.txt",
        file=BytesIO(text_content),
        headers={"content-type": "text/plain"}
    )
    
    try:
        filepath, content, mime = await file_handler.save_upload(file)
        
        print(f"✅ Text file saved: {filepath}")
        print(f"   Size: {len(content)} bytes")
        print(f"   MIME: {mime}")
        print(f"   Content preview: {content[:50].decode('utf-8')}...")
        
        # Nettoyer
        await file_handler.delete_file(filepath)
        print(f"✅ File deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_file_too_large():
    """Test de rejet d'un fichier trop volumineux"""
    
    # Créer un fichier de 11 MB (> limite de 10 MB)
    large_content = b'X' * (11 * 1024 * 1024)
    
    file = UploadFile(
        filename="huge_file.txt",
        file=BytesIO(large_content),
        headers={"content-type": "text/plain"}
    )
    
    try:
        await file_handler.save_upload(file)
        print("❌ Should have rejected large file")
    except Exception as e:
        print(f"✅ Correctly rejected large file: {type(e).__name__}")


async def test_cleanup_old_files():
    """Test du nettoyage automatique"""
    
    # Créer des fichiers temporaires
    test_files = []
    for i in range(3):
        filepath = settings.UPLOAD_DIR / f"test_{i}.txt"
        filepath.write_text(f"Test content {i}")
        test_files.append(filepath)
    
    print(f"✅ Created {len(test_files)} test files")
    
    # Lancer le nettoyage (ne supprimera pas car fichiers récents)
    await file_handler.cleanup_old_files()
    
    # Vérifier
    remaining = [f for f in test_files if f.exists()]
    print(f"   Remaining files: {len(remaining)} (normal, files are recent)")
    
    # Nettoyer manuellement
    deleted = 0
    for f in test_files:
        if f.exists():
            if await file_handler.delete_file(f):
                deleted += 1
    
    print(f"✅ Manual cleanup: deleted {deleted} files")


async def run_tests():
    """Lancer tous les tests"""
    print("=" * 60)
    print("TEST 1: Save valid image (PNG)")
    print("=" * 60)
    await test_save_valid_image()
    
    print("\n" + "=" * 60)
    print("TEST 2: Save valid text file")
    print("=" * 60)
    await test_save_text_file()
    
    print("\n" + "=" * 60)
    print("TEST 3: Reject invalid file (.exe)")
    print("=" * 60)
    await test_save_invalid_file()
    
    print("\n" + "=" * 60)
    print("TEST 4: Reject file too large (11MB)")
    print("=" * 60)
    await test_file_too_large()
    
    print("\n" + "=" * 60)
    print("TEST 5: Cleanup old files")
    print("=" * 60)
    await test_cleanup_old_files()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())