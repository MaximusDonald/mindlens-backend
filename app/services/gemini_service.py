"""
Service d'analyse avec Gemini 3
Gère l'appel à l'API, le parsing des réponses et la gestion des erreurs
"""
import logging
import re
from typing import Dict, List, Optional
import base64
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.config import settings
from app.prompts.analysis_prompts import AnalysisPrompts

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Analyseur intelligent basé sur Gemini 3"""
    
    def __init__(self):
        """Initialise le service Gemini"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Configuration du modèle
            self.model = genai.GenerativeModel(
                model_name='gemma-3-27b-it',  # Gemini 2.0 Flash (le plus rapide)
                generation_config={
                    'temperature': 0.7,  # Équilibre créativité/précision
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            
            # Configuration de sécurité (permissive pour analyse technique)
            self.safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            logger.info("Gemini service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise
    
    async def analyze_image(
        self, 
        image_bytes: bytes, 
        analysis_type: str,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, any]:
        """
        Analyse une image avec Gemini
        
        Args:
            image_bytes: Contenu binaire de l'image
            analysis_type: Type d'analyse ("infrastructure", "data", "document")
            mime_type: Type MIME de l'image
            
        Returns:
            Dict avec la structure d'analyse
        """
        try:
            # Préparer le prompt
            prompt = AnalysisPrompts.get_prompt_for_type(analysis_type)
            
            # Préparer l'image au format attendu par Gemini (inline_data en snake_case)
            image_part = {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64.standard_b64encode(image_bytes).decode("utf-8")
                }
            }
            
            logger.info(f"Analyzing image ({len(image_bytes)} bytes) with type: {analysis_type}")
            
            # Appel à Gemini
            response = self.model.generate_content(
                [prompt, image_part],
                safety_settings=self.safety_settings
            )
            
            # Parser la réponse
            result = self._parse_response(response.text)
            
            logger.info("Image analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            raise Exception(f"Erreur lors de l'analyse de l'image: {str(e)}")
    
    async def analyze_text(
        self, 
        text_content: str, 
        analysis_type: str
    ) -> Dict[str, any]:
        """
        Analyse un texte avec Gemini
        
        Args:
            text_content: Contenu textuel à analyser
            analysis_type: Type d'analyse
            
        Returns:
            Dict avec la structure d'analyse
        """
        try:
            # Préparer le prompt
            base_prompt = AnalysisPrompts.get_prompt_for_type(analysis_type)
            
            # Limiter la taille du texte (10000 caractères max)
            if len(text_content) > 10000:
                text_content = text_content[:10000] + "\n\n[...texte tronqué...]"
            
            full_prompt = f"{base_prompt}\n\n=== CONTENU À ANALYSER ===\n\n{text_content}"
            
            logger.info(f"Analyzing text ({len(text_content)} chars) with type: {analysis_type}")
            
            # Appel à Gemini
            response = self.model.generate_content(
                full_prompt,
                safety_settings=self.safety_settings
            )
            
            # Parser la réponse
            result = self._parse_response(response.text)
            
            logger.info("Text analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            raise Exception(f"Erreur lors de l'analyse du texte: {str(e)}")
    
    def _parse_response(self, raw_response: str) -> Dict[str, any]:
        """
        Parse la réponse structurée de Gemini
        
        Args:
            raw_response: Texte brut de la réponse
            
        Returns:
            Dict structuré avec observations, analysis, reasoning, actions
        """
        try:
            result = {
                "observations": "",
                "analysis": "",
                "reasoning": "",
                "actions": [],
                "raw_response": raw_response  # Pour debug
            }
            
            # Extraire les sections avec regex
            sections = {
                "observations": r"## 1\. OBSERVATIONS\s*\n(.*?)(?=## 2\. ANALYSE|$)",
                "analysis": r"## 2\. ANALYSE\s*\n(.*?)(?=## 3\. RAISONNEMENT|$)",
                "reasoning": r"## 3\. RAISONNEMENT\s*\n(.*?)(?=## 4\. ACTIONS|$)",
                "actions": r"## 4\. ACTIONS RECOMMANDÉES\s*\n(.*?)$"
            }
            
            for key, pattern in sections.items():
                match = re.search(pattern, raw_response, re.DOTALL | re.IGNORECASE)
                if match:
                    content = match.group(1).strip()
                    
                    if key == "actions":
                        # Extraire les actions comme liste
                        actions = re.findall(r'^[-•]\s*(.+)$', content, re.MULTILINE)
                        result["actions"] = [action.strip() for action in actions if action.strip()]
                    else:
                        result[key] = content
            
            # Validation : vérifier qu'on a au moins du contenu
            if not any([result["observations"], result["analysis"], result["reasoning"]]):
                logger.warning("Parsed response is empty, using raw response")
                # Fallback : utiliser la réponse brute
                result["observations"] = raw_response
                result["analysis"] = "Analyse générée sans structure définie."
                result["reasoning"] = "Le format de réponse n'a pas pu être parsé correctement."
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            # Fallback en cas d'échec total
            return {
                "observations": raw_response,
                "analysis": "Erreur de parsing de la réponse",
                "reasoning": str(e),
                "actions": [],
                "raw_response": raw_response
            }
    
    async def test_connection(self) -> bool:
        """
        Test la connexion à Gemini
        
        Returns:
            True si la connexion fonctionne
        """
        try:
            response = self.model.generate_content("Réponds simplement 'OK' si tu me reçois.")
            return "ok" in response.text.lower()
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False


# Instance globale du service
gemini_analyzer = GeminiAnalyzer()