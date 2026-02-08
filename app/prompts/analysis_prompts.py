"""
Templates de prompts structurés pour Gemini
Chaque type d'analyse a son contexte et ses instructions spécifiques
"""

class AnalysisPrompts:
    """Générateur de prompts structurés pour différents types d'analyse"""
    
    # Structure de base pour toutes les analyses
    BASE_STRUCTURE = """
Analyse ce contenu selon cette structure EXACTE en français :

## 1. OBSERVATIONS
Liste 5-7 points factuels clés que tu observes. Sois précis et concret.
Chaque point doit commencer par un tiret (-).

## 2. ANALYSE
Identifie 3-4 insights ou implications importantes.
Quels patterns ou tendances détectes-tu ?
Chaque insight doit commencer par un tiret (-).

## 3. RAISONNEMENT
Explique ta chaîne logique : comment es-tu passé des observations aux insights ?
Pourquoi ces conclusions ? Quel est le lien de causalité ?
Rédige en 2-3 paragraphes cohérents.

## 4. ACTIONS RECOMMANDÉES
Propose 3-5 actions concrètes et priorisées.
Chaque action doit être :
- Spécifique et actionnable
- Mesurable si possible
- Réaliste
Format : chaque action commence par un tiret (-).

IMPORTANT :
- Reste factuel et précis
- Évite les généralités vagues
- Priorise les recommandations (urgent → long terme)
- Utilise un langage professionnel mais accessible
"""
    
    @staticmethod
    def get_infrastructure_prompt() -> str:
        """
        Prompt pour l'analyse d'infrastructure et situations réelles
        (routes, bâtiments, espaces publics, sécurité)
        """
        context = """
CONTEXTE : Tu analyses une infrastructure ou situation réelle (route, bâtiment, espace public, équipement).

OBJECTIF : Identifier les problèmes, évaluer les risques et proposer des solutions pratiques.

FOCUS SPÉCIFIQUE :
- Sécurité : Quels dangers immédiats ou potentiels ?
- État structurel : Dégradation, usure, défauts visibles
- Impact : Qui est affecté ? Quelle est l'urgence ?
- Causes probables : Pourquoi cette situation ?
- Solutions : Actions correctives hiérarchisées par priorité
"""
        return context + AnalysisPrompts.BASE_STRUCTURE
    
    @staticmethod
    def get_data_prompt() -> str:
        """
        Prompt pour l'analyse de données visuelles
        (graphiques, tableaux, statistiques, tendances)
        """
        context = """
CONTEXTE : Tu analyses des données visuelles (graphique, tableau, statistique, dashboard).

OBJECTIF : Interpréter les tendances, détecter les anomalies et proposer des décisions stratégiques.

FOCUS SPÉCIFIQUE :
- Tendances : Évolution dans le temps, patterns récurrents
- Anomalies : Points atypiques, ruptures, incohérences
- Corrélations : Relations entre variables
- Implications : Que signifient ces données pour la prise de décision ?
- Prédictions : Évolution probable si la tendance continue
- Recommandations : Actions basées sur les données
"""
        return context + AnalysisPrompts.BASE_STRUCTURE
    
    @staticmethod
    def get_document_prompt() -> str:
        """
        Prompt pour l'analyse de documents texte
        (rapports, articles, études, synthèses)
        """
        context = """
CONTEXTE : Tu analyses un document texte (rapport, article, étude, note stratégique).

OBJECTIF : Extraire les idées clés, identifier les contradictions et synthétiser avec recommandations.

FOCUS SPÉCIFIQUE :
- Idées principales : Thèses centrales du document
- Arguments clés : Preuves et justifications avancées
- Contradictions : Incohérences internes ou avec des faits connus
- Forces/Faiblesses : Qualité de l'argumentation
- Implications pratiques : Comment utiliser ces informations ?
- Points manquants : Qu'est-ce qui n'est pas abordé ?
"""
        return context + AnalysisPrompts.BASE_STRUCTURE
    
    @staticmethod
    def get_prompt_for_type(analysis_type: str) -> str:
        """
        Retourne le prompt approprié selon le type d'analyse
        
        Args:
            analysis_type: "infrastructure", "data", ou "document"
            
        Returns:
            Prompt structuré complet
        """
        prompts = {
            "infrastructure": AnalysisPrompts.get_infrastructure_prompt(),
            "data": AnalysisPrompts.get_data_prompt(),
            "document": AnalysisPrompts.get_document_prompt()
        }
        
        return prompts.get(analysis_type, AnalysisPrompts.get_infrastructure_prompt())