"""
Tests pour le service Gemini
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import asyncio
from app.services.gemini_service import gemini_analyzer


async def test_connection():
    """Test de connexion à Gemini"""
    print("Testing Gemini connection...")
    
    try:
        is_connected = await gemini_analyzer.test_connection()
        
        if is_connected:
            print("✅ Gemini connection successful")
        else:
            print("❌ Gemini connection failed")
            
    except Exception as e:
        print(f"❌ Connection test error: {e}")


async def test_text_analysis():
    """Test d'analyse de texte"""
    print("\nTesting text analysis...")
    
    test_text = """
    Rapport sur l'état des routes de la ville
    
    Les routes principales présentent des signes de dégradation avancée.
    Plusieurs nids-de-poule ont été identifiés sur l'Avenue de la République.
    Le revêtement de la Route Nationale 5 montre des fissures importantes.
    
    Le budget alloué cette année est de 2 millions d'euros.
    Les réparations urgentes sont estimées à 3.5 millions d'euros.
    """
    
    try:
        result = await gemini_analyzer.analyze_text(
            text_content=test_text,
            analysis_type="infrastructure"
        )
        
        print("✅ Text analysis completed")
        print(f"\n📊 OBSERVATIONS ({len(result['observations'])} chars):")
        print(result['observations'][:200] + "..." if len(result['observations']) > 200 else result['observations'])
        
        print(f"\n🔍 ANALYSIS ({len(result['analysis'])} chars):")
        print(result['analysis'][:200] + "..." if len(result['analysis']) > 200 else result['analysis'])
        
        print(f"\n🧠 REASONING ({len(result['reasoning'])} chars):")
        print(result['reasoning'][:200] + "..." if len(result['reasoning']) > 200 else result['reasoning'])
        
        print(f"\n✅ ACTIONS ({len(result['actions'])} items):")
        for i, action in enumerate(result['actions'][:3], 1):
            print(f"   {i}. {action}")
        
    except Exception as e:
        print(f"❌ Text analysis error: {e}")
        import traceback
        traceback.print_exc()


async def test_image_analysis():
    """Test d'analyse d'image (avec une vraie petite image)"""
    print("\nTesting image analysis...")
    
    # Générer une vraie image PNG 100x100 pixels (petit carré gris)
    # C'est une image PNG valide bien plus acceptable par Gemini qu'un pixel
    try:
        from PIL import Image
        import io
        
        # Créer une image 100x100 gris
        img = Image.new('RGB', (100, 100), color='gray')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        png_bytes = img_byte_arr.getvalue()
    except ImportError:
        # Si PIL n'est pas disponible, utiliser une vraie image PNG 8x8 pixels minimaliste
        png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x08\x00\x00\x00\x08\x08\x02\x00\x00\x00kw\x0bw\x00\x00\x00\x1dIDATx\x9cc\xf8\xcf\xc0\x00\x03\x03\x03\x00\x00\x00\xff\x00\x00\x01&\x00!\xef\x9b2\x00\x00\x00\x00IEND\xaeB`\x82'
    
    try:
        result = await gemini_analyzer.analyze_image(
            image_bytes=png_bytes,
            analysis_type="infrastructure",
            mime_type="image/png"
        )
        
        print("✅ Image analysis completed")
        print(f"\n📊 OBSERVATIONS:")
        print(result['observations'][:300] + "..." if len(result['observations']) > 300 else result['observations'])
        
        print(f"\n✅ ACTIONS ({len(result['actions'])} items):")
        for i, action in enumerate(result['actions'][:3], 1):
            print(f"   {i}. {action}")
        
    except Exception as e:
        print(f"❌ Image analysis error: {e}")
        import traceback
        traceback.print_exc()


async def run_tests():
    """Lancer tous les tests"""
    print("=" * 60)
    print("GEMINI SERVICE TESTS")
    print("=" * 60)
    
    await test_connection()
    await test_text_analysis()
    await test_image_analysis()
    
    print("\n" + "=" * 60)
    print("✅ GEMINI TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())