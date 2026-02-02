<script lang="ts">
    // Page À propos
</script>

<svelte:head>
    <title>À propos - EasyJobFind AI</title>
    <meta
        name="description"
        content="Découvrez comment EasyJobFind utilise l'intelligence artificielle pour vous aider à trouver l'emploi idéal."
    />
</svelte:head>

<div class="about-page">
    <!-- Hero Section -->
    <section class="about-hero">
        <div class="container">
            <span class="hero-badge">À propos</span>
            <h1>
                L'IA au service de
                <span class="text-gradient">votre carrière</span>
            </h1>
            <p class="hero-description">
                EasyJobFind combine l'intelligence artificielle de pointe avec
                les offres officielles de France Travail pour vous aider à
                trouver l'emploi qui vous correspond vraiment.
            </p>
        </div>
    </section>

    <!-- How it works -->
    <section class="how-it-works">
        <div class="container">
            <div class="section-header">
                <h2>Comment ça fonctionne ?</h2>
                <p>Un processus simple et efficace en 3 étapes</p>
            </div>

            <div class="steps">
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <div class="step-icon">📄</div>
                        <h3>Upload de votre CV</h3>
                        <p>
                            Déposez votre CV au format PDF. Notre système
                            extrait automatiquement le texte de votre document
                            de manière sécurisée.
                        </p>
                    </div>
                </div>

                <div class="step-connector">
                    <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                    >
                        <path d="M12 5v14m7-7l-7 7-7-7" />
                    </svg>
                </div>

                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <div class="step-icon">🧠</div>
                        <h3>Analyse par l'IA Groq</h3>
                        <p>
                            Notre IA propulsée par Groq analyse votre CV pour
                            identifier votre métier, vos compétences clés, votre
                            niveau d'expérience et vos points forts.
                        </p>
                    </div>
                </div>

                <div class="step-connector">
                    <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                    >
                        <path d="M12 5v14m7-7l-7 7-7-7" />
                    </svg>
                </div>

                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <div class="step-icon">🎯</div>
                        <h3>Matching avec France Travail</h3>
                        <p>
                            Nous interrogeons l'API officielle de France Travail
                            pour trouver les offres qui correspondent à votre
                            profil, avec un score de matching personnalisé.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Technologies -->
    <section class="technologies">
        <div class="container">
            <div class="section-header">
                <h2>Technologies utilisées</h2>
                <p>Une stack moderne et performante</p>
            </div>

            <div class="tech-grid">
                <div class="tech-card card">
                    <div class="tech-logo">⚡</div>
                    <h3>Groq AI</h3>
                    <p>LPU ultra-rapide pour l'analyse de CV en temps réel</p>
                </div>

                <div class="tech-card card">
                    <div class="tech-logo">🏛️</div>
                    <h3>France Travail API</h3>
                    <p>Accès aux offres d'emploi officielles</p>
                </div>

                <div class="tech-card card">
                    <div class="tech-logo">🚀</div>
                    <h3>FastAPI</h3>
                    <p>Backend Python haute performance</p>
                </div>

                <div class="tech-card card">
                    <div class="tech-logo">🎨</div>
                    <h3>SvelteKit</h3>
                    <p>Frontend moderne et réactif</p>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
        <div class="container">
            <div class="cta-card">
                <h2>Prêt à trouver votre job idéal ?</h2>
                <p>Déposez votre CV et laissez l'IA faire le reste</p>
                <a href="/" class="btn btn-primary">
                    <span>🎯</span>
                    <span>Analyser mon CV</span>
                </a>
            </div>
        </div>
    </section>
</div>

<style>
    .about-page {
        padding-bottom: 4rem;
    }

    /* Hero */
    .about-hero {
        padding: 5rem 0;
        text-align: center;
        background: linear-gradient(
            180deg,
            rgba(99, 102, 241, 0.05) 0%,
            transparent 100%
        );
    }

    .hero-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 50px;
        font-size: 0.8125rem;
        font-weight: 600;
        color: var(--primary-light);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1.5rem;
    }

    .about-hero h1 {
        font-size: clamp(2rem, 4vw, 3rem);
        margin-bottom: 1.5rem;
    }

    .hero-description {
        max-width: 640px;
        margin: 0 auto;
        font-size: 1.125rem;
        color: var(--text-secondary);
        line-height: 1.7;
    }

    /* Section header */
    .section-header {
        text-align: center;
        margin-bottom: 3rem;
    }

    .section-header h2 {
        margin-bottom: 0.5rem;
    }

    .section-header p {
        color: var(--text-muted);
    }

    /* How it works */
    .how-it-works {
        padding: 5rem 0;
    }

    .steps {
        max-width: 600px;
        margin: 0 auto;
    }

    .step {
        display: flex;
        gap: 1.5rem;
        padding: 2rem;
        background: var(--bg-card);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-xl);
        backdrop-filter: blur(12px);
    }

    .step-number {
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--gradient-primary);
        border-radius: 50%;
        font-size: 1.25rem;
        font-weight: 700;
        color: white;
        flex-shrink: 0;
    }

    .step-content {
        flex: 1;
    }

    .step-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
    }

    .step-content h3 {
        font-size: 1.25rem;
        margin-bottom: 0.5rem;
    }

    .step-content p {
        color: var(--text-secondary);
        font-size: 0.9375rem;
        line-height: 1.6;
    }

    .step-connector {
        display: flex;
        justify-content: center;
        padding: 1rem 0;
        color: var(--primary);
        opacity: 0.5;
    }

    /* Technologies */
    .technologies {
        padding: 5rem 0;
        background: linear-gradient(
            180deg,
            transparent 0%,
            rgba(99, 102, 241, 0.03) 100%
        );
    }

    .tech-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.5rem;
    }

    .tech-card {
        text-align: center;
        padding: 2rem;
    }

    .tech-logo {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }

    .tech-card h3 {
        font-size: 1.125rem;
        margin-bottom: 0.5rem;
    }

    .tech-card p {
        color: var(--text-muted);
        font-size: 0.9375rem;
    }

    /* CTA */
    .cta-section {
        padding: 3rem 0;
    }

    .cta-card {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(
            135deg,
            rgba(99, 102, 241, 0.1) 0%,
            rgba(139, 92, 246, 0.1) 100%
        );
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: var(--radius-2xl);
    }

    .cta-card h2 {
        font-size: 1.75rem;
        margin-bottom: 0.5rem;
    }

    .cta-card p {
        color: var(--text-secondary);
        margin-bottom: 2rem;
    }

    .cta-card .btn {
        padding: 1rem 2.5rem;
    }

    @media (max-width: 640px) {
        .step {
            flex-direction: column;
            text-align: center;
        }

        .step-number {
            margin: 0 auto;
        }
    }
</style>
