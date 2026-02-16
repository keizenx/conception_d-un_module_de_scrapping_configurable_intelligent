# backend/src/core/llm_classifier.py
import os
import json
import requests
from typing import Dict, Any, Optional

class LLMClassifier:
    """
    Classificateur sémantique utilisant un LLM (Perplexity, OpenAI, etc.) 
    pour comprendre le contenu d'une page web complexe.
    """
    
    def __init__(self, provider: str = "perplexity", api_key: Optional[str] = None):
        self.provider = provider
        # Support both generic LLM_API_KEY and specific PERPLEXITY_API_KEY
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("PERPLEXITY_API_KEY")
        self.api_url = "https://api.perplexity.ai/chat/completions" if provider == "perplexity" else "https://api.openai.com/v1/chat/completions"
        
        # Strip 'pplx-' prefix if it was pasted incorrectly (sometimes happens)
        if self.api_key and self.api_key.startswith('pplx-') and len(self.api_key) > 60:
             # Just a safety check, usually pplx- is correct but let's ensure no whitespace
             self.api_key = self.api_key.strip()

    def analyze_page(self, url: str, page_text: str, detected_candidates: list) -> Dict[str, Any]:
        """
        Analyse le contexte de la page via LLM pour valider et affiner les types détectés.
        """
        if not self.api_key:
            print(f"[*] Pas de clé API pour {self.provider}, passage en mode heuristique uniquement.")
            return None

        # On limite le texte envoyé pour ne pas exploser le contexte
        context = page_text[:2000] + "..." + page_text[-500:]
        
        system_prompt = """
        Tu es un expert en analyse de sites web et classification sémantique.
        Ton objectif est d'analyser le contenu textuel d'une page d'accueil pour comprendre la nature profonde du site.
        
        Tu dois générer une réponse au format JSON STRICT respectant le schéma suivant :
        {
            "url": "L'URL analysée",
            "titre": "Titre supposé du site",
            "description_générale": "Une phrase descriptive du type 'Ce site web semble être...'",
            "catégorie_principale": "La catégorie macro (ex: E-commerce, Blog, Vitrine, SaaS...)",
            "services_proposés": ["Liste", "des", "services", "ou", "produits", "principaux"],
            "type_de_contenu": ["Types", "de", "contenu", "détectés", "ex: articles, produits, vidéos"],
            "confiance_de_classification": 0.0 à 1.0,
            "suggested_selectors": ["sélecteur css probable pour le contenu principal"]
        }
        
        Sois précis et descriptif. Ne te limite pas à des catégories génériques, décris ce que fait réellement le site.
        """

        user_prompt = f"""
        URL: {url}
        Candidats détectés par regex: {json.dumps(detected_candidates)}
        
        Début du contenu textuel de la page:
        {context}
        """

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar-pro" if self.provider == "perplexity" else "gpt-4-turbo-preview",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1
            }

            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Nettoyage du JSON (au cas où le LLM bavarde autour)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            return json.loads(content.strip())

        except Exception as e:
            print(f"[-] Erreur LLM Classifier: {e}")
            return None
