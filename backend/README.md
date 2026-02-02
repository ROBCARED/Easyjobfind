# EasyJobFind API

API backend pour l'analyse de CV et la recherche d'offres d'emploi France Travail.

## Déploiement sur Render

1. Créez un compte sur [render.com](https://render.com)
2. Cliquez sur "New" > "Web Service"
3. Connectez votre repository GitHub
4. Sélectionnez le dossier `backend`
5. Configurez les variables d'environnement :
   - `GROQ_API_KEY` : Votre clé API Groq
   - `FT_CLIENT_ID` : Votre Client ID France Travail
   - `FT_CLIENT_SECRET` : Votre Client Secret France Travail

## Variables d'environnement requises

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Clé API Groq pour l'analyse IA |
| `FT_CLIENT_ID` | Client ID de l'API France Travail |
| `FT_CLIENT_SECRET` | Secret de l'API France Travail |

## Endpoints

- `POST /analyze` - Analyse un CV (PDF) et retourne les offres correspondantes
- `GET /jobs/{keyword}` - Recherche des offres par mot-clé
- `GET /health` - Vérification de l'état du serveur
