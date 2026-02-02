from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import fitz  # PyMuPDF
import services
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EasyJobFind API",
    description="API pour l'analyse de CV et la recherche d'emploi",
    version="2.0.0"
)

# CORS pour le frontend (dev + production)
import os
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, remplacer par votre domaine Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic
class ProfileResponse(BaseModel):
    metier_recherche: str
    competences_cles: List[str]
    points_forts: List[str]
    niveau_experience: Optional[str] = "junior"

class JobOffer(BaseModel):
    id: str
    intitule: str
    entreprise: dict
    lieuTravail: dict
    description: str
    url: str
    salaire: Optional[str] = None
    contrat: Optional[str] = None

class AnalyzeResponse(BaseModel):
    profile: ProfileResponse
    jobs: List[JobOffer]

@app.get("/")
async def root():
    return {"message": "EasyJobFind API v2.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_cv(file: UploadFile = File(...)):
    """
    Analyse un CV (PDF) et retourne le profil détecté + les offres correspondantes
    """
    # Vérifier le type de fichier
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Le fichier doit être un PDF")
    
    try:
        # Lire le contenu du PDF
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        text_cv = "".join([page.get_text() for page in doc])
        doc.close()
        
        if not text_cv.strip():
            raise HTTPException(status_code=400, detail="Le PDF ne contient pas de texte extractible")
        
        logger.info(f"CV reçu: {file.filename}, {len(text_cv)} caractères")
        
        # Analyser le CV avec Groq
        profile_data = services.analyse_cv_with_groq(text_cv)
        
        if not profile_data:
            raise HTTPException(status_code=500, detail="Erreur lors de l'analyse du CV")
        
        # Rechercher les offres avec le nouveau matching intelligent
        jobs_data = services.fetch_jobs_with_matching(profile_data)
        
        # Construire la réponse
        profile = ProfileResponse(
            metier_recherche=profile_data.get('metier_recherche', 'Inconnu'),
            competences_cles=profile_data.get('competences_cles', []),
            points_forts=profile_data.get('points_forts', []),
            niveau_experience=profile_data.get('niveau_experience', 'junior')
        )
        
        jobs = [
            JobOffer(
                id=j['id'],
                intitule=j['intitule'],
                entreprise=j['entreprise'],
                lieuTravail=j['lieuTravail'],
                description=j['description'],
                url=j['url'],
                salaire=j.get('salaire'),
                contrat=j.get('contrat')
            )
            for j in jobs_data
        ]
        
        logger.info(f"Analyse terminée: {len(jobs)} offres trouvées pour '{profile_data.get('metier_recherche', 'inconnu')}'")
        
        return AnalyzeResponse(profile=profile, jobs=jobs)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur analyse: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.get("/jobs/{keyword}", response_model=List[JobOffer])
async def search_jobs(keyword: str):
    """
    Recherche des offres d'emploi par mot-clé
    """
    jobs_data = services.fetch_real_jobs(None, keyword)
    
    return [
        JobOffer(
            id=j['id'],
            intitule=j['intitule'],
            entreprise=j['entreprise'],
            lieuTravail=j['lieuTravail'],
            description=j['description'],
            url=j['url'],
            salaire=j.get('salaire'),
            contrat=j.get('contrat')
        )
        for j in jobs_data
    ]

@app.get("/health")
async def health_check():
    """Endpoint de vérification de l'état du serveur"""
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
