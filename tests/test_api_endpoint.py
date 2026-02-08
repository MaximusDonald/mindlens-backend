"""
Tests pour les endpoints de l'API
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import asyncio
from io import BytesIO
from httpx import AsyncClient, ASGITransport
from app.main import app


async def test_health_endpoint():
    """Test du health check"""
    print("Testing /health endpoint...")
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        print(f"✅ Health check: {data['status']}")
        print(f"   Gemini configured: {data['gemini_configured']}")


async def test_analysis_types_endpoint():
    """Test de l'endpoint des types d'analyse"""
    print("\nTesting /api/analysis-types endpoint...")
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/analysis-types")
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"✅ Analysis types: {len(data['types'])} types available")
        for t in data['types']:
            print(f"   - {t['value']}: {t['label']}")


async def test_analyze_text_endpoint():
    """Test de l'analyse d'un fichier texte"""
    print("\nTesting /api/analyze endpoint (text file)...")
    
    # Créer un fichier texte de test
    test_content = b"""
    Rapport d'inspection de la route nationale 7
    
    Constat: Degradation importante du revetement.
    Nids-de-poule nombreux sur 500m.
    Risque eleve pour la securite routiere.
    Budget necessaire: 150000 euros.
    """
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("test_report.txt", BytesIO(test_content), "text/plain")}
        data = {"analysis_type": "infrastructure"}
        
        response = await client.post("/api/analyze", files=files, data=data)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis completed")
            print(f"   Observations: {len(result['observations'])} chars")
            print(f"   Actions: {len(result['actions'])} items")
            
            if result['actions']:
                print(f"   First action: {result['actions'][0][:80]}...")
        else:
            print(f"❌ Error: {response.json()}")


async def run_tests():
    """Lancer tous les tests"""
    print("=" * 60)
    print("API ENDPOINT TESTS")
    print("=" * 60)
    
    await test_health_endpoint()
    await test_analysis_types_endpoint()
    await test_analyze_text_endpoint()
    
    print("\n" + "=" * 60)
    print("✅ API TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    # Installer httpx si pas déjà fait: pip install httpx
    asyncio.run(run_tests())