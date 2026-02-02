# EasyJobFind 🚀

Application de recherche d'emploi intelligente propulsée par l'IA.

## 🎯 Fonctionnalités

- **Analyse de CV par IA** : Extraction automatique des compétences et du profil
- **Matching intelligent** : Score de compatibilité avec les offres France Travail
- **Interface moderne** : Design premium et responsive

## 🏗️ Architecture

```
EasyJobFind/
├── backend/          # API FastAPI
│   ├── main.py       # Endpoints API
│   ├── services.py   # Logique métier
│   └── config.py     # Configuration
└── frontend/         # SvelteKit
    └── src/
        └── routes/   # Pages
```

## 🚀 Déploiement

### Backend (Render)

1. Créez un compte sur [render.com](https://render.com)
2. New > Web Service > Connectez votre repo GitHub
3. Root Directory: `backend`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
6. Variables d'environnement requises :
   - `GROQ_API_KEY`
   - `FT_CLIENT_ID`
   - `FT_CLIENT_SECRET`

### Frontend (Vercel)

1. Créez un compte sur [vercel.com](https://vercel.com)
2. Add New > Project > Importez votre repo
3. Root Directory: `frontend`
4. Variables d'environnement :
   - `PUBLIC_API_URL` = URL de votre backend Render

## 🔧 Développement local

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## 📝 Variables d'environnement

### Backend (.env)
```
GROQ_API_KEY=votre_clé_groq
FT_CLIENT_ID=votre_client_id
FT_CLIENT_SECRET=votre_secret
```

### Frontend (.env)
```
PUBLIC_API_URL=http://localhost:8000
```

## 📄 Licence

MIT - Libre d'utilisation