import os
from dotenv import load_dotenv
from groq import Groq

# Charger les variables d'environnement (depuis .env en local, via le platform en production)
load_dotenv()

# Identifiants et clés (doivent être configurées dans .env)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FT_ID = os.getenv("FT_CLIENT_ID")
FT_SECRET = os.getenv("FT_CLIENT_SECRET")

# Validation des clés requises
if not GROQ_API_KEY:
    raise ValueError("⚠️ GROQ_API_KEY manquante! Ajoutez-la dans le fichier .env")

# Initialize Groq client
client_groq = Groq(api_key=GROQ_API_KEY)

# URLS API France Travail
AUTH_URL = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi"
