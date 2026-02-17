import os
from dotenv import load_dotenv
from groq import Groq

# Charger les variables d'environnement (depuis .env en local, via le platform en production)
load_dotenv()

# Identifiants et clés (doivent être configurées dans .env)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FT_ID = os.getenv("FT_CLIENT_ID")
FT_SECRET = os.getenv("FT_CLIENT_SECRET")

# Validation des clés requises (warning au lieu de crash pour Vercel build)
if not GROQ_API_KEY:
    import logging
    logging.warning("⚠️ GROQ_API_KEY manquante! L'analyse IA ne fonctionnera pas.")

# Initialize Groq client (conditionnel pour éviter le crash au build)
client_groq = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# URLS API France Travail
AUTH_URL = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi"
