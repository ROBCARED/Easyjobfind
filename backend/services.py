import requests
import base64
import json
import logging
import config
import time

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_ft_token():
    """Récupère le jeton d'accès OAuth2."""
    if not config.FT_ID or not config.FT_SECRET:
        return None

    user_pass = f"{config.FT_ID.strip()}:{config.FT_SECRET.strip()}"
    auth_b64 = base64.b64encode(user_pass.encode()).decode()

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {auth_b64}'
    }
    data = {"grant_type": "client_credentials", "scope": "api_offresdemploiv2 o2dsoffre"}

    try:
        r = requests.post(config.AUTH_URL, data=data, headers=headers)
        if r.status_code == 200:
            logger.info("Token France Travail obtenu avec succès")
            return r.json().get("access_token")
        else:
            logger.warning(f"Échec auth France Travail: {r.status_code}")
            return None
    except Exception as e:
        logger.error(f"Erreur auth France Travail: {e}")
        return None

def fetch_jobs_with_matching(profile: dict):
    """
    Récupère les offres d'emploi avec un matching intelligent basé sur le profil.
    
    Args:
        profile: Dictionnaire contenant metier_recherche, competences_cles, niveau_experience
    
    Returns:
        Liste d'offres triées par score de matching
    """
    metier = profile.get('metier_recherche', 'emploi')
    competences = profile.get('competences_cles', [])
    niveau = profile.get('niveau_experience', 'junior')
    
    # Essayer l'API France Travail avec plusieurs stratégies de recherche
    token = get_ft_token()
    offres = []
    
    if token:
        # Stratégie 1: Recherche avec le métier complet
        offres = fetch_france_travail_jobs(token, metier)
        
        # Stratégie 2: Si pas de résultats, essayer avec le premier mot significatif
        if not offres and len(metier.split()) > 1:
            premier_mot = [m for m in metier.split() if len(m) > 3]
            if premier_mot:
                logger.info(f"Retry recherche avec mot-clé: '{premier_mot[0]}'")
                offres = fetch_france_travail_jobs(token, premier_mot[0])
        
        # Stratégie 3: Essayer avec les compétences clés
        if not offres and competences:
            keyword = competences[0] if competences else 'emploi'
            logger.info(f"Retry recherche avec compétence: '{keyword}'")
            offres = fetch_france_travail_jobs(token, keyword)
        
        # Stratégie 4: Recherche générique
        if not offres:
            logger.info("Retry recherche générique: 'emploi'")
            offres = fetch_france_travail_jobs(token, 'emploi')
    
    if not offres:
        logger.warning("Aucune offre France Travail trouvée après toutes les stratégies")
        return []
    
    # Calculer le score de matching pour chaque offre
    scored_jobs = []
    for job in offres:
        score = calculate_matching_score(job, metier, competences, niveau)
        job['matching_score'] = score
        scored_jobs.append(job)
    
    # Trier par score décroissant
    scored_jobs.sort(key=lambda x: x['matching_score'], reverse=True)
    
    # Retourner les 5 meilleures offres
    top_jobs = scored_jobs[:5]
    
    logger.info(f"Top 5 jobs pour '{metier}': scores = {[j['matching_score'] for j in top_jobs]}")
    
    return top_jobs

def calculate_matching_score(job: dict, metier: str, competences: list, niveau: str) -> int:
    """
    Calcule un score de matching entre une offre et le profil.
    
    Score basé sur:
    - Correspondance du titre/métier (0-40 points)
    - Correspondance des compétences (0-40 points)
    - Correspondance du niveau (0-20 points)
    """
    score = 0
    
    job_title = job.get('intitule', '').lower()
    job_desc = job.get('description', '').lower()
    job_text = f"{job_title} {job_desc}"
    
    # 1. Score métier (40 points max)
    metier_lower = metier.lower()
    metier_words = metier_lower.split()
    
    for word in metier_words:
        if len(word) > 2:  # Ignorer les mots trop courts
            if word in job_title:
                score += 20
            elif word in job_desc:
                score += 10
    
    # Limiter à 40 points
    score = min(score, 40)
    
    # 2. Score compétences (40 points max, 8 points par compétence trouvée)
    competences_score = 0
    for comp in competences:
        comp_lower = comp.lower()
        if comp_lower in job_text:
            competences_score += 8
    
    score += min(competences_score, 40)
    
    # 3. Score niveau d'expérience (20 points max)
    job_niveau = job.get('niveau', 'tous')
    
    niveau_keywords = {
        'junior': ['junior', 'débutant', 'stage', 'alternance', 'apprenti'],
        'intermediaire': ['confirmé', '2 ans', '3 ans', 'intermédiaire'],
        'senior': ['senior', 'expert', 'lead', '5 ans', '10 ans', 'expérimenté']
    }
    
    if job_niveau == 'tous' or job_niveau == niveau:
        score += 15
    elif niveau in niveau_keywords:
        for keyword in niveau_keywords[niveau]:
            if keyword in job_text:
                score += 20
                break
    
    return score

def fetch_real_jobs(token, keyword, profile=None):
    """
    Récupère les offres d'emploi depuis l'API France Travail.
    Si un profil est fourni, utilise le matching intelligent.
    """
    if profile:
        return fetch_jobs_with_matching(profile)
    
    search_term = keyword.strip() if keyword else "emploi"
    
    # Obtenir le token si non fourni
    if not token:
        token = get_ft_token()
    
    # Essayer l'API France Travail
    if token:
        offres = fetch_france_travail_jobs(token, search_term)
        if offres:
            return offres
    
    # Pas de résultats France Travail
    logger.warning("API France Travail indisponible ou aucun résultat")
    return []

def fetch_france_travail_jobs(token: str, keyword: str, max_results: int = 20):
    """
    Récupère les offres d'emploi depuis l'API France Travail v2.
    
    Args:
        token: Token OAuth2 d'accès
        keyword: Mot-clé de recherche
        max_results: Nombre maximum de résultats (défaut: 20)
    
    Returns:
        Liste d'offres d'emploi au format normalisé
    """
    try:
        # URL de l'API France Travail v2
        api_url = f"{config.SEARCH_URL}/v2/offres/search"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Paramètres de recherche
        params = {
            'motsCles': keyword,
            'range': f'0-{max_results - 1}'  # Format: start-end (0-indexed)
        }
        
        logger.info(f"Recherche France Travail: '{keyword}'")
        
        response = requests.get(api_url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            resultats = data.get('resultats', [])
            
            logger.info(f"{len(resultats)} offres France Travail trouvées")
            
            # Normaliser les résultats au format attendu par l'application
            offres = []
            for offre_ft in resultats:
                offre = normalize_france_travail_job(offre_ft)
                offres.append(offre)
            
            return offres
        
        elif response.status_code == 206:
            # Réponse partielle (moins de résultats que demandé)
            data = response.json()
            resultats = data.get('resultats', [])
            logger.info(f"{len(resultats)} offres France Travail (résultats partiels)")
            
            offres = []
            for offre_ft in resultats:
                offre = normalize_france_travail_job(offre_ft)
                offres.append(offre)
            
            return offres
        
        else:
            logger.warning(f"Erreur API France Travail: {response.status_code} - {response.text[:200]}")
            return []
            
    except requests.exceptions.Timeout:
        logger.warning("Timeout API France Travail")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur requête France Travail: {e}")
        return []
    except Exception as e:
        logger.error(f"Erreur inattendue France Travail: {e}")
        return []

def normalize_france_travail_job(offre_ft: dict) -> dict:
    """
    Normalise une offre France Travail au format interne de l'application.
    
    Args:
        offre_ft: Offre au format API France Travail
    
    Returns:
        Offre au format normalisé pour l'application
    """
    # Extraire les informations de l'entreprise
    entreprise_info = offre_ft.get('entreprise', {})
    nom_entreprise = entreprise_info.get('nom', 'Entreprise non précisée')
    
    # Extraire le lieu de travail
    lieu_travail = offre_ft.get('lieuTravail', {})
    lieu_libelle = lieu_travail.get('libelle', 'France')
    
    # Construire la description
    description = offre_ft.get('description', '')
    if not description:
        description = offre_ft.get('appellationlibelle', 'Offre d\'emploi France Travail')
    # Limiter la description à 500 caractères
    if len(description) > 500:
        description = description[:497] + '...'
    
    # Construire l'URL de l'offre
    job_id = offre_ft.get('id', '')
    url_offre = f"https://candidat.francetravail.fr/offres/recherche/detail/{job_id}"
    
    # Extraire le salaire si disponible
    salaire = None
    salaire_info = offre_ft.get('salaire', {})
    if salaire_info:
        libelle_salaire = salaire_info.get('libelle')
        if libelle_salaire:
            salaire = libelle_salaire
        else:
            # Essayer de construire à partir de min/max
           commentaire = salaire_info.get('commentaire')
           if commentaire:
                salaire = commentaire
    
    # Extraire le type de contrat
    contrat = offre_ft.get('typeContratLibelle', offre_ft.get('typeContrat', 'Non précisé'))
    
    # Déterminer le niveau d'expérience
    experience = offre_ft.get('experienceLibelle', '').lower()
    niveau = 'tous'
    if any(word in experience for word in ['débutant', 'moins de 1 an', 'sans expérience']):
        niveau = 'junior'
    elif any(word in experience for word in ['1 an', '2 ans', '3 ans']):
        niveau = 'intermediaire'
    elif any(word in experience for word in ['5 ans', '10 ans', 'expérimenté', 'senior']):
        niveau = 'senior'
    
    # Extraire les compétences/tags si disponibles
    tags = []
    competences = offre_ft.get('competences', [])
    for comp in competences[:5]:  # Limiter à 5 compétences
        if isinstance(comp, dict):
            tags.append(comp.get('libelle', ''))
        elif isinstance(comp, str):
            tags.append(comp)
    
    return {
        'id': job_id,
        'intitule': offre_ft.get('intitule', 'Offre d\'emploi'),
        'entreprise': {'nom': nom_entreprise},
        'lieuTravail': {'libelle': lieu_libelle},
        'description': description,
        'url': url_offre,
        'salaire': salaire,
        'contrat': contrat,
        'niveau': niveau,
        'tags': tags
    }

def get_all_mock_jobs():
    """Retourne TOUTES les offres mock pour le matching"""
    all_jobs = [
        # DÉVELOPPEURS
        {
            "id": "job_001",
            "intitule": "Développeur Python Senior",
            "entreprise": {"nom": "TechCorp Solutions"},
            "lieuTravail": {"libelle": "Paris (75)"},
            "description": "Développeur Python senior avec 5+ années d'expérience. Stack: Python, FastAPI, Django, PostgreSQL, Docker, API REST, machine learning.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=developpeur+python+paris",
            "salaire": "55-70k€",
            "contrat": "CDI",
            "niveau": "senior",
            "tags": ["python", "fastapi", "django", "postgresql", "docker", "api", "backend"]
        },
        {
            "id": "job_002",
            "intitule": "Développeur Full Stack React/Node.js",
            "entreprise": {"nom": "StartUp Innovante"},
            "lieuTravail": {"libelle": "Lyon (69)"},
            "description": "Développeur Full Stack sur notre plateforme SaaS. Stack: React, TypeScript, Node.js, MongoDB, GraphQL, AWS.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=developpeur+fullstack+react",
            "salaire": "45-55k€",
            "contrat": "CDI",
            "niveau": "intermediaire",
            "tags": ["react", "javascript", "typescript", "nodejs", "mongodb", "fullstack", "frontend", "backend"]
        },
        {
            "id": "job_003",
            "intitule": "Développeur Java Spring Boot",
            "entreprise": {"nom": "Groupe Financier France"},
            "lieuTravail": {"libelle": "Paris - La Défense (92)"},
            "description": "Développeur Java pour applications bancaires. Java 17, Spring Boot, microservices, Kubernetes. Télétravail 3j/semaine.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=developpeur+java",
            "salaire": "50-65k€",
            "contrat": "CDI",
            "niveau": "intermediaire",
            "tags": ["java", "spring", "springboot", "microservices", "kubernetes", "backend"]
        },
        {
            "id": "job_004",
            "intitule": "Développeur Mobile Flutter/Dart",
            "entreprise": {"nom": "Mobile First Agency"},
            "lieuTravail": {"libelle": "Toulouse (31)"},
            "description": "Applications mobiles multi-plateforme avec Flutter, Dart, Firebase, REST APIs. Android et iOS.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=developpeur+mobile+flutter",
            "salaire": "40-50k€",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["flutter", "dart", "mobile", "android", "ios", "firebase"]
        },
        {
            "id": "job_005",
            "intitule": "DevOps Engineer AWS/Kubernetes",
            "entreprise": {"nom": "Cloud Provider Européen"},
            "lieuTravail": {"libelle": "Bordeaux (33)"},
            "description": "Infrastructure cloud AWS. Kubernetes, Terraform, CI/CD, Jenkins, GitLab CI. Télétravail 100%.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=devops+engineer",
            "salaire": "50-70k€",
            "contrat": "CDI",
            "niveau": "senior",
            "tags": ["devops", "aws", "kubernetes", "terraform", "docker", "cicd", "jenkins"]
        },
        {
            "id": "job_006",
            "intitule": "Développeur Frontend Vue.js",
            "entreprise": {"nom": "E-commerce Tech"},
            "lieuTravail": {"libelle": "Nantes (44)"},
            "description": "Développeur Frontend Vue.js 3, Nuxt, TypeScript, Tailwind CSS. Interfaces utilisateur modernes.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=developpeur+vuejs",
            "salaire": "42-52k€",
            "contrat": "CDI",
            "niveau": "intermediaire",
            "tags": ["vuejs", "vue", "javascript", "typescript", "nuxt", "frontend", "css"]
        },
        {
            "id": "job_007",
            "intitule": "Développeur PHP Laravel",
            "entreprise": {"nom": "Agence Web Créative"},
            "lieuTravail": {"libelle": "Marseille (13)"},
            "description": "Développeur PHP Laravel, MySQL, WordPress. Sites web et applications métier.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=developpeur+php+laravel",
            "salaire": "38-48k€",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["php", "laravel", "mysql", "wordpress", "backend", "web"]
        },
        {
            "id": "job_008",
            "intitule": "Développeur .NET C# Senior",
            "entreprise": {"nom": "Industrie Française SA"},
            "lieuTravail": {"libelle": "Strasbourg (67)"},
            "description": "Développeur C# .NET Core, Azure, SQL Server. Applications industrielles.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=developpeur+dotnet",
            "salaire": "55-68k€",
            "contrat": "CDI",
            "niveau": "senior",
            "tags": ["csharp", "dotnet", ".net", "azure", "sqlserver", "backend"]
        },
        
        # DATA
        {
            "id": "job_101",
            "intitule": "Data Engineer Python/Spark",
            "entreprise": {"nom": "Big Data Corp"},
            "lieuTravail": {"libelle": "Paris (75)"},
            "description": "Data Engineer pour pipelines de données. Python, PySpark, Kafka, AWS, Airflow, ETL.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=data+engineer",
            "salaire": "50-65k€",
            "contrat": "CDI",
            "niveau": "intermediaire",
            "tags": ["python", "spark", "pyspark", "kafka", "aws", "airflow", "data", "etl"]
        },
        {
            "id": "job_102",
            "intitule": "Data Scientist Machine Learning",
            "entreprise": {"nom": "AI Solutions Inc"},
            "lieuTravail": {"libelle": "Lille (59)"},
            "description": "Data Scientist ML. Python, TensorFlow, PyTorch, scikit-learn, deep learning, NLP.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=data+scientist",
            "salaire": "50-65k€",
            "contrat": "CDI",
            "niveau": "intermediaire",
            "tags": ["python", "tensorflow", "pytorch", "machinelearning", "ml", "data", "nlp", "deeplearning"]
        },
        {
            "id": "job_103",
            "intitule": "Data Analyst SQL/Tableau",
            "entreprise": {"nom": "E-commerce Leader"},
            "lieuTravail": {"libelle": "Paris (75)"},
            "description": "Data Analyst débutant accepté. Excel, SQL, Tableau, Power BI. Formation interne.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=data+analyst",
            "salaire": "35-45k€",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["sql", "excel", "tableau", "powerbi", "data", "analytics"]
        },
        {
            "id": "job_104",
            "intitule": "Machine Learning Engineer",
            "entreprise": {"nom": "Tech AI Startup"},
            "lieuTravail": {"libelle": "Lyon (69)"},
            "description": "ML Engineer pour déploiement de modèles. Python, MLOps, Docker, Kubernetes, AWS SageMaker.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=ml+engineer",
            "salaire": "55-75k€",
            "contrat": "CDI",
            "niveau": "senior",
            "tags": ["python", "machinelearning", "mlops", "docker", "kubernetes", "aws"]
        },
        
        # DESIGN
        {
            "id": "job_201",
            "intitule": "UX/UI Designer",
            "entreprise": {"nom": "Digital Agency"},
            "lieuTravail": {"libelle": "Nantes (44)"},
            "description": "UX/UI Designer interfaces web et mobile. Figma, Adobe XD, prototypage, wireframes.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=ux+ui+designer",
            "salaire": "40-50k€",
            "contrat": "CDI",
            "niveau": "intermediaire",
            "tags": ["ux", "ui", "figma", "adobexd", "design", "prototyping"]
        },
        {
            "id": "job_202",
            "intitule": "Product Designer",
            "entreprise": {"nom": "SaaS Company"},
            "lieuTravail": {"libelle": "Montpellier (34)"},
            "description": "Product Designer pour plateforme SaaS. Design system, user research, Figma.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=product+designer",
            "salaire": "50-65k€",
            "contrat": "CDI",
            "niveau": "senior",
            "tags": ["ux", "ui", "product", "figma", "design", "designsystem"]
        },
        {
            "id": "job_203",
            "intitule": "Graphiste / Designer Graphique",
            "entreprise": {"nom": "Studio Créatif"},
            "lieuTravail": {"libelle": "Paris (75)"},
            "description": "Graphiste pour identités visuelles. Adobe Creative Suite, Illustrator, Photoshop, InDesign.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=graphiste",
            "salaire": "32-42k€",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["graphisme", "illustrator", "photoshop", "indesign", "adobe", "design"]
        },
        
        # MARKETING DIGITAL
        {
            "id": "job_301",
            "intitule": "Chef de Projet Digital",
            "entreprise": {"nom": "Agence 360"},
            "lieuTravail": {"libelle": "Paris (75)"},
            "description": "Gestion de projets digitaux, coordination équipes, méthodologie Agile, Scrum.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=chef+projet+digital",
            "salaire": "45-55k€",
            "contrat": "CDI",
            "niveau": "intermediaire",
            "tags": ["gestion", "projet", "agile", "scrum", "digital", "management"]
        },
        {
            "id": "job_302",
            "intitule": "Traffic Manager / SEA",
            "entreprise": {"nom": "Performance Agency"},
            "lieuTravail": {"libelle": "Lyon (69)"},
            "description": "Traffic Manager Google Ads, Facebook Ads, LinkedIn Ads. Optimisation campagnes.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=traffic+manager",
            "salaire": "38-48k€",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["sea", "googleads", "facebookads", "marketing", "digital", "ads"]
        },
        {
            "id": "job_303",
            "intitule": "SEO Manager",
            "entreprise": {"nom": "Content Agency"},
            "lieuTravail": {"libelle": "Bordeaux (33)"},
            "description": "SEO Manager pour stratégie référencement. SEO technique, content marketing, analytics.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=seo+manager",
            "salaire": "40-52k€",
            "contrat": "CDI",
            "niveau": "intermediaire",
            "tags": ["seo", "referencement", "content", "marketing", "analytics", "digital"]
        },
        
        # CYBERSÉCURITÉ
        {
            "id": "job_401",
            "intitule": "Ingénieur Cybersécurité",
            "entreprise": {"nom": "SecureTech"},
            "lieuTravail": {"libelle": "Paris (75)"},
            "description": "Ingénieur sécurité. Pentesting, audit, SIEM, SOC, ISO 27001, gestion des vulnérabilités.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=cybersecurite",
            "salaire": "50-70k€",
            "contrat": "CDI",
            "niveau": "intermediaire",
            "tags": ["securite", "cybersecurite", "pentest", "soc", "siem", "audit"]
        },
        
        # RÉSEAU / SYSTÈME
        {
            "id": "job_501",
            "intitule": "Administrateur Système Linux",
            "entreprise": {"nom": "Hébergeur Cloud"},
            "lieuTravail": {"libelle": "Roubaix (59)"},
            "description": "Admin sys Linux, Ansible, scripts Bash, monitoring, Docker, virtualisation.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=administrateur+systeme+linux",
            "salaire": "42-55k€",
            "contrat": "CDI",
            "niveau": "intermediaire",
            "tags": ["linux", "ansible", "bash", "docker", "sysadmin", "systeme"]
        },
        
        # ==========================================
        # VENTE / COMMERCE / RETAIL
        # ==========================================
        {
            "id": "job_601",
            "intitule": "Vendeur / Vendeuse Polyvalent(e)",
            "entreprise": {"nom": "Carrefour"},
            "lieuTravail": {"libelle": "Noisy-le-Grand (93)"},
            "description": "Accueil et conseil client, mise en rayon, gestion des stocks, encaissement. Expérience en grande distribution appréciée.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=vendeur+carrefour",
            "salaire": "1800-2000€/mois",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["vente", "vendeur", "vendeuse", "commerce", "retail", "magasin", "client", "accueil", "rayon", "caisse", "encaissement"]
        },
        {
            "id": "job_602",
            "intitule": "Employé(e) Libre-Service",
            "entreprise": {"nom": "Auchan"},
            "lieuTravail": {"libelle": "Paris (75)"},
            "description": "Mise en rayon, réapprovisionnement, facing, contrôle des dates. Travail en équipe, dynamisme requis.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=employe+libre+service",
            "salaire": "1750-1900€/mois",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["rayon", "mise en rayon", "stock", "magasin", "supermarché", "grande distribution", "commerce"]
        },
        {
            "id": "job_603",
            "intitule": "Caissier / Caissière",
            "entreprise": {"nom": "Monoprix"},
            "lieuTravail": {"libelle": "Lyon (69)"},
            "description": "Encaissement, accueil client, fidélisation. Sens du service, rapidité et rigueur.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=caissier",
            "salaire": "1750-1850€/mois",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["caisse", "caissier", "encaissement", "client", "accueil", "commerce", "magasin"]
        },
        {
            "id": "job_604",
            "intitule": "Conseiller(ère) de Vente Mode",
            "entreprise": {"nom": "Zara"},
            "lieuTravail": {"libelle": "Paris - Forum des Halles"},
            "description": "Conseil personnalisé, vente de vêtements, merchandising, stocks. Passionné(e) de mode.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=conseiller+vente+mode",
            "salaire": "1850-2100€/mois",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["mode", "vêtements", "fashion", "vente", "conseil", "client", "boutique", "textile"]
        },
        {
            "id": "job_605",
            "intitule": "Vendeur(se) High-Tech",
            "entreprise": {"nom": "Fnac Darty"},
            "lieuTravail": {"libelle": "Marseille (13)"},
            "description": "Vente téléphones, ordinateurs, TV. Conseil technique, SAV. Connaissance produits tech.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=vendeur+fnac",
            "salaire": "1900-2200€/mois",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["high-tech", "téléphone", "informatique", "électronique", "vente", "conseil", "tech"]
        },
        
        # ==========================================
        # ACCUEIL / RÉCEPTION
        # ==========================================
        {
            "id": "job_701",
            "intitule": "Agent d'Accueil",
            "entreprise": {"nom": "Mairie de Paris"},
            "lieuTravail": {"libelle": "Paris (75)"},
            "description": "Accueil du public, orientation, renseignements. Maîtrise du français, sens du service public.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=agent+accueil",
            "salaire": "1800-2000€/mois",
            "contrat": "CDD",
            "niveau": "junior",
            "tags": ["accueil", "réception", "public", "orientation", "renseignement", "service"]
        },
        {
            "id": "job_702",
            "intitule": "Réceptionniste Hôtel",
            "entreprise": {"nom": "Ibis Hotels"},
            "lieuTravail": {"libelle": "Nice (06)"},
            "description": "Accueil clients, check-in/check-out, réservations, standard téléphonique. Anglais requis.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=receptionniste+hotel",
            "salaire": "1900-2100€/mois",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["hotel", "accueil", "réception", "tourisme", "client", "réservation", "anglais"]
        },
        {
            "id": "job_703",
            "intitule": "Hôte/Hôtesse d'Accueil Entreprise",
            "entreprise": {"nom": "Groupe Elior"},
            "lieuTravail": {"libelle": "La Défense (92)"},
            "description": "Accueil visiteurs, gestion badges, standard, courrier. Présentation soignée.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=hotesse+accueil",
            "salaire": "1800-2000€/mois",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["accueil", "hôtesse", "visiteurs", "entreprise", "standard", "réception"]
        },
        
        # ==========================================
        # RESTAURATION / HÔTELLERIE
        # ==========================================
        {
            "id": "job_801",
            "intitule": "Serveur / Serveuse Restaurant",
            "entreprise": {"nom": "Groupe Bertrand"},
            "lieuTravail": {"libelle": "Paris (75)"},
            "description": "Service en salle, prise de commandes, conseil client. Dynamisme, sourire.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=serveur+restaurant",
            "salaire": "1800-2200€/mois + pourboires",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["serveur", "serveuse", "restaurant", "service", "salle", "restauration", "client"]
        },
        {
            "id": "job_802",
            "intitule": "Équipier(ère) Polyvalent(e) Fast-Food",
            "entreprise": {"nom": "McDonald's"},
            "lieuTravail": {"libelle": "Toute France"},
            "description": "Préparation commandes, service comptoir, nettoyage. Travail en équipe, horaires flexibles.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=equipier+mcdonalds",
            "salaire": "1750-1850€/mois",
            "contrat": "CDI/CDD",
            "niveau": "junior",
            "tags": ["fast-food", "restauration", "équipier", "cuisine", "service", "comptoir"]
        },
        {
            "id": "job_803",
            "intitule": "Barman / Barmaid",
            "entreprise": {"nom": "Bar Cocktails Paris"},
            "lieuTravail": {"libelle": "Paris 11ème"},
            "description": "Préparation cocktails, service bar, accueil clients. Connaissance mixologie appréciée.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=barman",
            "salaire": "1900-2300€/mois",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["bar", "barman", "barmaid", "cocktails", "service", "boissons", "nuit"]
        },
        {
            "id": "job_804",
            "intitule": "Cuisinier(ère)",
            "entreprise": {"nom": "Restaurant Traditionnel"},
            "lieuTravail": {"libelle": "Bordeaux (33)"},
            "description": "Préparation plats, mise en place, normes HACCP. CAP Cuisine requis.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=cuisinier",
            "salaire": "2000-2500€/mois",
            "contrat": "CDI",
            "niveau": "intermediaire",
            "tags": ["cuisine", "cuisinier", "restaurant", "chef", "plats", "gastronomie"]
        },
        
        # ==========================================
        # LOGISTIQUE / MANUTENTION
        # ==========================================
        {
            "id": "job_901",
            "intitule": "Préparateur de Commandes",
            "entreprise": {"nom": "Amazon"},
            "lieuTravail": {"libelle": "Saran (45)"},
            "description": "Préparation colis, emballage, scan produits. Travail debout, port de charges.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=preparateur+commandes+amazon",
            "salaire": "1850-2000€/mois",
            "contrat": "CDI/Intérim",
            "niveau": "junior",
            "tags": ["logistique", "préparateur", "commandes", "entrepôt", "colis", "manutention"]
        },
        {
            "id": "job_902",
            "intitule": "Manutentionnaire",
            "entreprise": {"nom": "Manpower"},
            "lieuTravail": {"libelle": "Île-de-France"},
            "description": "Chargement/déchargement, tri colis, picking. CACES apprécié.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=manutentionnaire",
            "salaire": "1800-2000€/mois",
            "contrat": "Intérim",
            "niveau": "junior",
            "tags": ["manutention", "logistique", "entrepôt", "cariste", "colis", "chargement"]
        },
        {
            "id": "job_903",
            "intitule": "Livreur / Livreuse",
            "entreprise": {"nom": "Chronopost"},
            "lieuTravail": {"libelle": "Paris et IDF"},
            "description": "Livraison colis, tournée, relation client. Permis B obligatoire.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=livreur",
            "salaire": "1900-2100€/mois",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["livreur", "livraison", "colis", "permis", "chauffeur", "transport"]
        },
        
        # ==========================================
        # JOBS ÉTUDIANTS / TEMPS PARTIEL
        # ==========================================
        {
            "id": "job_1001",
            "intitule": "Job Étudiant - Vendeur Week-end",
            "entreprise": {"nom": "Decathlon"},
            "lieuTravail": {"libelle": "Noisy-le-Grand (93)"},
            "description": "Vente articles sport, conseil client. Samedi/Dimanche. Passionné de sport.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=job+etudiant+vendeur",
            "salaire": "11.65€/h",
            "contrat": "CDD Temps partiel",
            "niveau": "junior",
            "tags": ["étudiant", "job étudiant", "weekend", "temps partiel", "vente", "sport"]
        },
        {
            "id": "job_1002",
            "intitule": "Job Étudiant - Équipier Restauration",
            "entreprise": {"nom": "Burger King"},
            "lieuTravail": {"libelle": "Paris"},
            "description": "Service client, préparation, nettoyage. Horaires flexibles, compatible études.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=job+etudiant+restauration",
            "salaire": "11.65€/h",
            "contrat": "CDD Temps partiel",
            "niveau": "junior",
            "tags": ["étudiant", "job étudiant", "restauration", "fast-food", "flexible"]
        },
        {
            "id": "job_1003",
            "intitule": "Job Étudiant - Hôte de Caisse",
            "entreprise": {"nom": "Leclerc"},
            "lieuTravail": {"libelle": "Région Parisienne"},
            "description": "Encaissement clients, accueil. Week-ends et vacances scolaires.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=job+etudiant+caisse",
            "salaire": "11.65€/h",
            "contrat": "CDD Temps partiel",
            "niveau": "junior",
            "tags": ["étudiant", "job étudiant", "caisse", "encaissement", "supermarché"]
        },
        
        # ==========================================
        # ADMINISTRATION / SECRÉTARIAT
        # ==========================================
        {
            "id": "job_1101",
            "intitule": "Assistant(e) Administratif(ve)",
            "entreprise": {"nom": "Cabinet Comptable"},
            "lieuTravail": {"libelle": "Paris (75)"},
            "description": "Gestion courrier, classement, accueil téléphonique, saisie données. Word, Excel.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=assistant+administratif",
            "salaire": "1900-2200€/mois",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["administratif", "secrétariat", "bureautique", "excel", "word", "accueil"]
        },
        {
            "id": "job_1102",
            "intitule": "Secrétaire Médical(e)",
            "entreprise": {"nom": "Centre Médical"},
            "lieuTravail": {"libelle": "Lille (59)"},
            "description": "Accueil patients, prise RDV, gestion dossiers médicaux. Discrétion requise.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=secretaire+medical",
            "salaire": "1850-2100€/mois",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["secrétaire", "médical", "santé", "accueil", "rdv", "patients"]
        },
        
        # ==========================================
        # NETTOYAGE / ENTRETIEN
        # ==========================================
        {
            "id": "job_1201",
            "intitule": "Agent d'Entretien",
            "entreprise": {"nom": "Onet Propreté"},
            "lieuTravail": {"libelle": "Île-de-France"},
            "description": "Nettoyage locaux, bureaux, parties communes. Autonomie, rigueur.",
            "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=agent+entretien",
            "salaire": "1750-1900€/mois",
            "contrat": "CDI",
            "niveau": "junior",
            "tags": ["nettoyage", "entretien", "propreté", "ménage", "bureaux"]
        }
    ]
    
    return all_jobs

def get_realistic_mock_jobs(keyword):
    """Retourne des offres filtrées par mot-clé (fallback simple)"""
    keyword_lower = keyword.lower()
    all_jobs = get_all_mock_jobs()
    
    # Filtrer les jobs qui matchent le keyword
    matching_jobs = []
    for job in all_jobs:
        job_text = f"{job['intitule']} {job['description']} {' '.join(job.get('tags', []))}".lower()
        if keyword_lower in job_text:
            matching_jobs.append(job)
    
    if matching_jobs:
        return matching_jobs[:5]
    
    # Si aucun match, retourner 5 jobs aléatoires
    import random
    return random.sample(all_jobs, min(5, len(all_jobs)))


def analyse_cv_with_groq(text_cv):
    """Analyse le CV via l'IA Groq."""
    
    # Log le début du texte du CV pour debug
    logger.info(f"Début de l'analyse CV ({len(text_cv)} caractères)")
    logger.debug(f"Extrait CV: {text_cv[:500]}...")
    
    prompt = f"""Tu es un expert en recrutement. Analyse attentivement ce CV et extrais les informations EXACTES mentionnées.

INSTRUCTIONS IMPORTANTES:
1. Lis TOUT le CV attentivement
2. Identifie le métier/poste recherché ou le dernier poste occupé
3. Liste TOUTES les technologies, outils et langages mentionnés explicitement
4. Évalue le niveau d'expérience basé sur les dates et postes

Renvoie STRICTEMENT un JSON valide avec ces champs:

{{
  "metier_recherche": "Le métier principal (ex: Développeur Web, Chef de Projet, Data Analyst)",
  "competences_cles": ["Liste de 5-10 compétences techniques EXACTES mentionnées dans le CV"],
  "langages": ["Langages de programmation mentionnés"],
  "outils": ["Outils et frameworks mentionnés"],
  "points_forts": ["3 points forts du candidat"],
  "niveau_experience": "junior|intermediaire|senior",
  "domaines": ["Domaines d'expertise: web, mobile, data, devops, etc."],
  "formations": ["Formations et diplômes mentionnés"]
}}

RÈGLES:
- N'invente RIEN, utilise uniquement ce qui est écrit dans le CV
- Si une technologie n'est pas mentionnée, ne l'ajoute pas
- Sois précis: "React" pas "JavaScript frameworks"

CV À ANALYSER:
{text_cv[:5000]}"""
    
    try:
        chat = config.client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Tu es un assistant expert en analyse de CV. Tu réponds uniquement en JSON valide."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1  # Basse température pour des résultats plus précis
        )
        
        result = json.loads(chat.choices[0].message.content)
        
        # Log détaillé du résultat
        logger.info(f"=== ANALYSE CV TERMINÉE ===")
        logger.info(f"Métier détecté: {result.get('metier_recherche', 'N/A')}")
        logger.info(f"Compétences: {result.get('competences_cles', [])}")
        logger.info(f"Langages: {result.get('langages', [])}")
        logger.info(f"Niveau: {result.get('niveau_experience', 'N/A')}")
        logger.info(f"Domaines: {result.get('domaines', [])}")
        
        # Fusionner langages et outils dans competences_cles pour le matching
        all_skills = result.get('competences_cles', [])
        all_skills.extend(result.get('langages', []))
        all_skills.extend(result.get('outils', []))
        result['competences_cles'] = list(set(all_skills))  # Dédupliquer
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur Groq: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fallback: essayer d'extraire des mots-clés basiques du CV
        return extract_basic_profile(text_cv)

def extract_basic_profile(text_cv):
    """Extraction basique si Groq échoue."""
    text_lower = text_cv.lower()
    
    # Détecter des technologies courantes
    tech_keywords = {
        'python': 'Python', 'java': 'Java', 'javascript': 'JavaScript',
        'react': 'React', 'angular': 'Angular', 'vue': 'Vue.js',
        'node': 'Node.js', 'php': 'PHP', 'sql': 'SQL',
        'docker': 'Docker', 'kubernetes': 'Kubernetes', 'aws': 'AWS',
        'git': 'Git', 'linux': 'Linux', 'mongodb': 'MongoDB',
        'postgresql': 'PostgreSQL', 'mysql': 'MySQL',
        'html': 'HTML', 'css': 'CSS', 'typescript': 'TypeScript',
        'c#': 'C#', '.net': '.NET', 'azure': 'Azure',
        'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch',
        'excel': 'Excel', 'power bi': 'Power BI', 'tableau': 'Tableau'
    }
    
    found_skills = []
    for keyword, name in tech_keywords.items():
        if keyword in text_lower:
            found_skills.append(name)
    
    # Détecter le métier
    metier = "Développeur"
    if 'data' in text_lower and ('scientist' in text_lower or 'analyst' in text_lower):
        metier = "Data Scientist"
    elif 'devops' in text_lower:
        metier = "DevOps Engineer"
    elif 'frontend' in text_lower or 'front-end' in text_lower:
        metier = "Développeur Frontend"
    elif 'backend' in text_lower or 'back-end' in text_lower:
        metier = "Développeur Backend"
    elif 'fullstack' in text_lower or 'full-stack' in text_lower:
        metier = "Développeur Full Stack"
    
    logger.info(f"FALLBACK - Métier: {metier}, Compétences: {found_skills}")
    
    return {
        "metier_recherche": metier,
        "competences_cles": found_skills if found_skills else ["Python", "JavaScript"],
        "points_forts": ["Adaptabilité", "Apprentissage", "Motivation"],
        "niveau_experience": "junior",
        "domaines": ["web"]
    }

