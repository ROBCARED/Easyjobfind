<script lang="ts">
	import { goto } from "$app/navigation";

	let file: File | null = null;
	let isDragging = false;
	let isLoading = false;
	let errorMessage = "";
	let loadingStep = 0;

	const loadingSteps = [
		{ emoji: "📄", text: "Lecture du CV..." },
		{ emoji: "🧠", text: "Analyse IA en cours..." },
		{ emoji: "🔍", text: "Recherche des offres..." },
		{ emoji: "✨", text: "Préparation des résultats..." },
	];

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
		const files = e.dataTransfer?.files;
		if (files && files[0]) validateAndSetFile(files[0]);
	}

	function handleFileSelect(e: Event) {
		const input = e.target as HTMLInputElement;
		if (input.files && input.files[0]) validateAndSetFile(input.files[0]);
	}

	function validateAndSetFile(f: File) {
		if (f.type !== "application/pdf") {
			errorMessage = "Seuls les fichiers PDF sont acceptés";
			return;
		}
		if (f.size > 10 * 1024 * 1024) {
			errorMessage = "Le fichier ne doit pas dépasser 10 Mo";
			return;
		}
		errorMessage = "";
		file = f;
	}

	// URL de l'API configurable via variable d'environnement
	const API_URL =
		import.meta.env.PUBLIC_API_URL || "https://easyjobfinds.vercel.app";

	async function analyzeCV() {
		if (!file) return;

		isLoading = true;
		errorMessage = "";
		loadingStep = 0;

		const stepInterval = setInterval(() => {
			if (loadingStep < loadingSteps.length - 1) loadingStep++;
		}, 1200);

		try {
			const formData = new FormData();
			formData.append("file", file);

			const response = await fetch(`${API_URL}/analyze`, {
				method: "POST",
				body: formData,
			});

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.detail || "Erreur lors de l'analyse");
			}

			const data = await response.json();
			sessionStorage.setItem("analysisResults", JSON.stringify(data));
			clearInterval(stepInterval);
			goto("/results");
		} catch (e) {
			errorMessage =
				e instanceof Error ? e.message : "Erreur de connexion";
			clearInterval(stepInterval);
		} finally {
			isLoading = false;
		}
	}

	function formatSize(bytes: number): string {
		if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " Ko";
		return (bytes / (1024 * 1024)).toFixed(1) + " Mo";
	}
</script>

<svelte:head>
	<title>EasyJobFind - Trouve ton job idéal grâce à l'IA</title>
	<meta
		name="description"
		content="Dépose ton CV et laisse notre IA trouver les offres France Travail qui te correspondent."
	/>
</svelte:head>

<!-- Hero Section -->
<section class="hero">
	<div class="hero-bg">
		<div class="hero-blob blob-1"></div>
		<div class="hero-blob blob-2"></div>
		<div class="hero-pattern"></div>
	</div>

	<div class="container hero-container">
		<div class="hero-content">
			<div class="hero-badge animate-fade-in-down">
				<span class="badge-dot"></span>
				<span>Propulsé par Groq AI</span>
			</div>

			<h1 class="animate-fade-in-up delay-1">
				Trouve ton <span class="text-gradient">emploi idéal</span> en quelques
				secondes
			</h1>

			<p class="hero-description animate-fade-in-up delay-2">
				Notre intelligence artificielle analyse ton CV et te propose les
				meilleures offres
				<strong>France Travail</strong> parfaitement adaptées à ton profil.
			</p>

			<div class="hero-stats animate-fade-in-up delay-3">
				<div class="stat-item">
					<span class="stat-number">10K+</span>
					<span class="stat-label">Offres analysées</span>
				</div>
				<div class="stat-divider"></div>
				<div class="stat-item">
					<span class="stat-number">95%</span>
					<span class="stat-label">Matching précis</span>
				</div>
				<div class="stat-divider"></div>
				<div class="stat-item">
					<span class="stat-number">&lt;5s</span>
					<span class="stat-label">Analyse rapide</span>
				</div>
			</div>
		</div>

		<div class="upload-section animate-fade-in-up delay-4">
			<div class="upload-card card card-elevated">
				<div class="upload-header">
					<h2>📄 Dépose ton CV</h2>
					<p>Format PDF • Max 10 Mo</p>
				</div>

				<div
					class="dropzone"
					class:dragging={isDragging}
					class:has-file={file}
					ondragover={(e) => {
						e.preventDefault();
						isDragging = true;
					}}
					ondragleave={() => (isDragging = false)}
					ondrop={handleDrop}
					role="button"
					tabindex="0"
				>
					{#if file}
						<div class="file-preview">
							<div class="file-icon-box">
								<svg
									width="24"
									height="24"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
								>
									<path
										d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
									/>
									<polyline points="14 2 14 8 20 8" />
									<line x1="16" y1="13" x2="8" y2="13" />
									<line x1="16" y1="17" x2="8" y2="17" />
								</svg>
							</div>
							<div class="file-info">
								<span class="file-name">{file.name}</span>
								<span class="file-size"
									>{formatSize(file.size)}</span
								>
							</div>
							<button
								class="file-remove"
								onclick={() => (file = null)}
							>
								<svg
									width="18"
									height="18"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
								>
									<line x1="18" y1="6" x2="6" y2="18" />
									<line x1="6" y1="6" x2="18" y2="18" />
								</svg>
							</button>
						</div>
					{:else}
						<div class="dropzone-content">
							<div class="upload-icon">
								<svg
									width="40"
									height="40"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="1.5"
								>
									<path
										d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"
									/>
									<polyline points="17 8 12 3 7 8" />
									<line x1="12" y1="3" x2="12" y2="15" />
								</svg>
							</div>
							<p class="drop-text">Glisse ton CV ici</p>
							<span class="drop-or">ou</span>
							<label class="browse-btn btn btn-outline btn-sm">
								<input
									type="file"
									accept=".pdf"
									onchange={handleFileSelect}
									hidden
								/>
								Parcourir
							</label>
						</div>
					{/if}
				</div>

				{#if errorMessage}
					<div class="error-message">
						<svg
							width="18"
							height="18"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<circle cx="12" cy="12" r="10" />
							<line x1="12" y1="8" x2="12" y2="12" />
							<line x1="12" y1="16" x2="12.01" y2="16" />
						</svg>
						{errorMessage}
					</div>
				{/if}

				<button
					class="btn btn-primary btn-lg analyze-btn"
					disabled={!file || isLoading}
					onclick={analyzeCV}
				>
					{#if isLoading}
						<span class="spinner"></span>
						{loadingSteps[loadingStep].emoji}
						{loadingSteps[loadingStep].text}
					{:else}
						🎯 Trouver mes offres
					{/if}
				</button>

				<p class="privacy-note">
					🔒 Ton CV est analysé de manière sécurisée
				</p>
			</div>
		</div>
	</div>
</section>

<!-- Features Section -->
<section class="features">
	<div class="container">
		<div class="section-header">
			<span class="badge">Comment ça marche</span>
			<h2>3 étapes simples vers ton prochain emploi</h2>
		</div>

		<div class="features-grid">
			<div class="feature-card card hover-lift">
				<div class="feature-number">01</div>
				<div class="feature-icon">📄</div>
				<h3>Dépose ton CV</h3>
				<p>
					Upload ton CV au format PDF. Ton document est traité de
					manière confidentielle.
				</p>
			</div>

			<div class="feature-card card hover-lift">
				<div class="feature-number">02</div>
				<div class="feature-icon">🧠</div>
				<h3>Analyse IA</h3>
				<p>
					Notre IA identifie tes compétences, ton expérience et le
					métier qui te correspond.
				</p>
			</div>

			<div class="feature-card card hover-lift">
				<div class="feature-number">03</div>
				<div class="feature-icon">🎯</div>
				<h3>Offres sur mesure</h3>
				<p>
					Reçois les offres France Travail avec un score de
					compatibilité personnalisé.
				</p>
			</div>
		</div>
	</div>
</section>

<!-- Trust Section -->
<section class="trust">
	<div class="container">
		<div class="trust-banner">
			<div class="trust-item">
				<svg
					width="24"
					height="24"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
				>
					<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
				</svg>
				<span>Données sécurisées</span>
			</div>
			<div class="trust-item">
				<svg
					width="24"
					height="24"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
				>
					<circle cx="12" cy="12" r="10" />
					<polyline points="12 6 12 12 16 14" />
				</svg>
				<span>Résultats en &lt; 5 secondes</span>
			</div>
			<div class="trust-item">
				<svg
					width="24"
					height="24"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
				>
					<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
					<polyline points="22 4 12 14.01 9 11.01" />
				</svg>
				<span>100% gratuit</span>
			</div>
		</div>
	</div>
</section>

<style>
	/* ===================================================
	   Hero Section
	   =================================================== */
	.hero {
		position: relative;
		min-height: calc(100vh - 64px);
		display: flex;
		align-items: center;
		padding: 4rem 0;
		overflow: hidden;
	}

	.hero-bg {
		position: absolute;
		inset: 0;
		overflow: hidden;
		pointer-events: none;
	}

	.hero-blob {
		position: absolute;
		border-radius: 50%;
		filter: blur(80px);
		opacity: 0.5;
	}

	.blob-1 {
		top: -20%;
		right: -10%;
		width: 600px;
		height: 600px;
		background: linear-gradient(
			135deg,
			rgba(79, 70, 229, 0.3) 0%,
			rgba(124, 58, 237, 0.2) 100%
		);
	}

	.blob-2 {
		bottom: -30%;
		left: -10%;
		width: 500px;
		height: 500px;
		background: linear-gradient(
			135deg,
			rgba(6, 182, 212, 0.2) 0%,
			rgba(16, 185, 129, 0.15) 100%
		);
	}

	.hero-pattern {
		position: absolute;
		inset: 0;
		background-image: radial-gradient(
			rgba(79, 70, 229, 0.08) 1px,
			transparent 1px
		);
		background-size: 24px 24px;
	}

	.hero-container {
		position: relative;
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 4rem;
		align-items: center;
	}

	.hero-content {
		max-width: 540px;
	}

	.hero-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background: rgba(79, 70, 229, 0.08);
		border: 1px solid rgba(79, 70, 229, 0.15);
		border-radius: var(--radius-full);
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--primary);
		margin-bottom: 1.5rem;
	}

	.badge-dot {
		width: 8px;
		height: 8px;
		background: var(--primary);
		border-radius: 50%;
		animation: pulse 2s infinite;
	}

	.hero h1 {
		font-size: clamp(2.25rem, 4.5vw, 3.5rem);
		font-weight: 800;
		line-height: 1.15;
		margin-bottom: 1.5rem;
		letter-spacing: -0.03em;
	}

	.hero-description {
		font-size: 1.125rem;
		color: var(--text-secondary);
		line-height: 1.7;
		margin-bottom: 2rem;
	}

	.hero-description strong {
		color: var(--primary);
	}

	.hero-stats {
		display: inline-flex;
		align-items: center;
		gap: 1.5rem;
		padding: 1.25rem 1.5rem;
		background: var(--bg-primary);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-xl);
		box-shadow: var(--shadow-md);
	}

	.stat-item {
		text-align: center;
	}

	.stat-number {
		display: block;
		font-size: 1.5rem;
		font-weight: 800;
		color: var(--primary);
		line-height: 1;
		margin-bottom: 0.25rem;
	}

	.stat-label {
		font-size: 0.75rem;
		color: var(--text-muted);
		font-weight: 500;
	}

	.stat-divider {
		width: 1px;
		height: 32px;
		background: var(--border-light);
	}

	/* ===================================================
	   Upload Section
	   =================================================== */
	.upload-section {
		max-width: 420px;
		justify-self: end;
	}

	.upload-card {
		padding: 2rem;
	}

	.upload-header {
		text-align: center;
		margin-bottom: 1.5rem;
	}

	.upload-header h2 {
		font-size: 1.25rem;
		margin-bottom: 0.25rem;
	}

	.upload-header p {
		font-size: 0.875rem;
		color: var(--text-muted);
	}

	.dropzone {
		border: 2px dashed var(--border-medium);
		border-radius: var(--radius-xl);
		padding: 2rem;
		text-align: center;
		transition: all 0.2s;
		cursor: pointer;
		background: var(--bg-secondary);
	}

	.dropzone:hover {
		border-color: var(--primary);
		background: rgba(79, 70, 229, 0.02);
	}

	.dropzone.dragging {
		border-color: var(--primary);
		background: rgba(79, 70, 229, 0.05);
		transform: scale(1.01);
	}

	.dropzone.has-file {
		border-style: solid;
		border-color: var(--success);
		background: rgba(16, 185, 129, 0.02);
	}

	.dropzone-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.75rem;
	}

	.upload-icon {
		width: 64px;
		height: 64px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: rgba(79, 70, 229, 0.08);
		border-radius: 50%;
		color: var(--primary);
		margin-bottom: 0.5rem;
	}

	.drop-text {
		font-weight: 600;
		color: var(--text-primary);
	}

	.drop-or {
		font-size: 0.8125rem;
		color: var(--text-muted);
	}

	.file-preview {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.file-icon-box {
		width: 48px;
		height: 48px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: rgba(16, 185, 129, 0.1);
		border-radius: var(--radius-md);
		color: var(--success);
	}

	.file-info {
		flex: 1;
		text-align: left;
	}

	.file-name {
		display: block;
		font-weight: 600;
		color: var(--text-primary);
		font-size: 0.9375rem;
	}

	.file-size {
		font-size: 0.8125rem;
		color: var(--text-muted);
	}

	.file-remove {
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: rgba(239, 68, 68, 0.1);
		border: none;
		border-radius: 50%;
		color: var(--error);
		cursor: pointer;
		transition: all 0.2s;
	}

	.file-remove:hover {
		background: rgba(239, 68, 68, 0.15);
	}

	.error-message {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1rem;
		background: rgba(239, 68, 68, 0.08);
		border: 1px solid rgba(239, 68, 68, 0.15);
		border-radius: var(--radius-md);
		margin-top: 1rem;
		font-size: 0.875rem;
		color: var(--error);
	}

	.analyze-btn {
		width: 100%;
		margin-top: 1.5rem;
	}

	.analyze-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none !important;
		box-shadow: none !important;
	}

	.privacy-note {
		text-align: center;
		font-size: 0.8125rem;
		color: var(--text-muted);
		margin-top: 1rem;
	}

	/* ===================================================
	   Features Section
	   =================================================== */
	.features {
		padding: 6rem 0;
		background: var(--bg-primary);
	}

	.section-header {
		text-align: center;
		margin-bottom: 3.5rem;
	}

	.section-header .badge {
		margin-bottom: 1rem;
	}

	.features-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 2rem;
	}

	.feature-card {
		position: relative;
		padding: 2rem;
		text-align: center;
	}

	.feature-number {
		position: absolute;
		top: 1rem;
		right: 1.25rem;
		font-size: 0.75rem;
		font-weight: 700;
		color: var(--primary);
		opacity: 0.4;
	}

	.feature-icon {
		font-size: 2.5rem;
		margin-bottom: 1rem;
	}

	.feature-card h3 {
		font-size: 1.125rem;
		margin-bottom: 0.5rem;
	}

	.feature-card p {
		font-size: 0.9375rem;
		color: var(--text-secondary);
	}

	/* ===================================================
	   Trust Section
	   =================================================== */
	.trust {
		padding: 3rem 0;
		background: var(--bg-secondary);
		border-top: 1px solid var(--border-light);
	}

	.trust-banner {
		display: flex;
		justify-content: center;
		gap: 3rem;
		flex-wrap: wrap;
	}

	.trust-item {
		display: flex;
		align-items: center;
		gap: 0.625rem;
		font-size: 0.9375rem;
		font-weight: 500;
		color: var(--text-secondary);
	}

	.trust-item svg {
		color: var(--primary);
	}

	/* ===================================================
	   Responsive
	   =================================================== */
	@media (max-width: 1024px) {
		.hero-container {
			grid-template-columns: 1fr;
			text-align: center;
		}

		.hero-content {
			max-width: 100%;
		}

		.hero-stats {
			justify-content: center;
		}

		.upload-section {
			max-width: 480px;
			justify-self: center;
		}

		.features-grid {
			grid-template-columns: 1fr;
			max-width: 400px;
			margin: 0 auto;
		}
	}

	@media (max-width: 640px) {
		.hero {
			padding: 2rem 0;
		}

		.hero-stats {
			flex-direction: column;
			gap: 1rem;
		}

		.stat-divider {
			width: 60px;
			height: 1px;
		}

		.trust-banner {
			flex-direction: column;
			align-items: center;
			gap: 1.5rem;
		}
	}
</style>
