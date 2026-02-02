import streamlit as st
import pymupdf
import services

# Configuration de la page
st.set_page_config(
    page_title="EasyJobFind AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé pour un design moderne
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Variables */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #8b5cf6;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
    }
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, var(--bg-dark) 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 50%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: var(--text-secondary);
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Upload zone */
    .uploadedFile {
        background: var(--bg-card) !important;
        border: 2px dashed var(--primary) !important;
        border-radius: 16px !important;
    }
    
    /* Job card styling */
    .job-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .job-card:hover {
        transform: translateY(-4px);
        border-color: var(--primary);
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2);
    }
    
    .job-title {
        color: var(--text-primary);
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .job-company {
        color: var(--accent);
        font-weight: 500;
    }
    
    .job-location {
        color: var(--text-secondary);
    }
    
    .job-description {
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.6;
        margin-top: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4);
    }
    
    /* Link button */
    .stLinkButton > a {
        background: linear-gradient(90deg, var(--success) 0%, #059669 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stLinkButton > a:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4) !important;
    }
    
    /* Info/Success/Warning boxes */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: var(--primary) !important;
    }
    
    /* Stats container */
    .stats-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .stat-box {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        text-align: center;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
    }
    
    .stat-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def render_job_card(job):
    """Affiche une carte d'offre stylisée."""
    company = job.get('entreprise', {}).get('nom', 'Entreprise confidentielle')
    location = job.get('lieuTravail', {}).get('libelle', 'France')
    description = job.get('description', 'Aucune description disponible')[:350]
    
    # Construire l'URL
    if job.get('url') and job['url'].startswith('http'):
        url = job['url']
    elif job['id'].startswith('mock_') or job['id'].startswith('job_'):
        search_term = job['intitule'].split()[0]
        url = f"https://candidat.francetravail.fr/offres/recherche?motsCles={search_term}"
    else:
        url = f"https://candidat.francetravail.fr/offres/recherche/detail/{job['id']}"
    
    st.markdown(f"""
    <div class="job-card">
        <div class="job-title">💼 {job['intitule']}</div>
        <div style="margin: 0.5rem 0;">
            <span class="job-company">🏢 {company}</span>
            <span style="margin: 0 1rem; color: #475569;">•</span>
            <span class="job-location">📍 {location}</span>
        </div>
        <div class="job-description">{description}...</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.link_button("🚀 Postuler maintenant", url, use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

# En-tête principal
st.markdown('<h1 class="main-header">🚀 EasyJobFind AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Trouve ton job idéal grâce à l\'intelligence artificielle</p>', unsafe_allow_html=True)

# Zone centrale
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### 📄 Étape 1 : Dépose ton CV")
    uploaded_file = st.file_uploader(
        "Glisse ton CV ici (format PDF)",
        type="pdf",
        help="Nous analysons ton CV pour trouver les meilleures offres correspondant à ton profil"
    )
    
    if uploaded_file:
        st.success("✅ CV chargé avec succès!")
        
        # Extraire le texte du PDF
        doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
        text_cv = "".join([page.get_text() for page in doc])
        
        st.markdown("### 🔍 Étape 2 : Lance la recherche")
        
        if st.button("🎯 Trouver mes offres idéales", use_container_width=True):
            
            # Analyse du CV
            with st.spinner("🤖 Analyse de ton CV en cours..."):
                try:
                    profil = services.analyse_cv_with_groq(text_cv)
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
                    profil = None
            
            if profil:
                metier = profil.get('metier_recherche', 'Emploi')
                competences = profil.get('competences_cles', [])
                
                # Afficher le profil détecté
                st.markdown("---")
                st.markdown("### 🎯 Profil détecté")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.info(f"**Métier recherché:** {metier}")
                with col_b:
                    if competences:
                        st.info(f"**Compétences:** {', '.join(competences[:5])}")
                
                # Recherche des offres
                with st.spinner("🔎 Recherche des meilleures offres..."):
                    offres = services.fetch_real_jobs(None, metier)
                
                if offres:
                    st.markdown("---")
                    st.markdown(f"### 🎉 {len(offres)} offres trouvées pour toi!")
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    for offre in offres:
                        render_job_card(offre)
                else:
                    st.warning("😕 Aucune offre trouvée pour le moment. Essaie avec un autre CV ou réessaie plus tard.")
            else:
                st.error("❌ Impossible d'analyser le CV. Vérifie que ta clé API Groq est valide.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem 0;">
    <p>Propulsé par <strong>Groq AI</strong> 🚀</p>
    <p style="font-size: 0.8rem;">EasyJobFind - Trouve ton emploi idéal avec l'IA</p>
</div>
""", unsafe_allow_html=True)