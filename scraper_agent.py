import anthropic
import schedule
import time
from datetime import datetime
import json

# Configuration
ANTHROPIC_API_KEY = "votre_cle_api_ici"
OUTPUT_FILE = "articles_presse_citron.json"

def scrape_presse_citron():
    """Récupère les articles de Presse Citron via Claude"""
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": """Récupère les 20 derniers articles de https://www.presse-citron.net/
                
Utilise web_fetch pour charger la page d'accueil.
Pour chaque article, extrais :
- Titre
- Résumé court (2-3 phrases)
- URL complète
- Catégorie

Retourne les résultats en format JSON uniquement, sans texte autour :
[
  {
    "titre": "...",
    "resume": "...",
    "url": "...",
    "categorie": "..."
  }
]"""
            }
        ]
    )
    
    # Extraire le contenu
    response_text = message.content[0].text
    
    # Parser le JSON
    try:
        # Nettoyer le texte pour extraire uniquement le JSON
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        json_data = json.loads(response_text[start:end])
        
        # Ajouter timestamp
        result = {
            "date_scraping": datetime.now().isoformat(),
            "nb_articles": len(json_data),
            "articles": json_data
        }
        
        # Sauvegarder
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {len(json_data)} articles récupérés - {datetime.now()}")
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ Erreur parsing JSON: {e}")
        return None

def job():
    """Tâche planifiée"""
    print(f"🤖 Lancement du scraping - {datetime.now()}")
    scrape_presse_citron()

# Programmer l'exécution quotidienne à 9h
schedule.every().day.at("09:00").do(job)

print("🚀 Agent démarré - Scraping quotidien à 9h00")
print("Appuyez sur Ctrl+C pour arrêter")

# Exécution immédiate au démarrage (optionnel)
job()

# Boucle principale
while True:
    schedule.run_pending()
    time.sleep(60)  # Vérifier toutes les minutes
