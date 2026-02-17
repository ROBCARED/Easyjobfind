<script lang="ts">
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";

	interface Job {
		id: string;
		intitule: string;
		entreprise: { nom: string };
		lieuTravail: { libelle: string };
		description: string;
		url: string;
		salaire?: string;
		contrat?: string;
		matching_score?: number;
	}

	interface Profile {
		metier_recherche: string;
		competences_cles: string[];
		points_forts: string[];
		niveau_experience: string;
	}

	interface AnalysisData {
		profile: Profile;
		jobs: Job[];
	}

	let data: AnalysisData | null = null;
	let filteredJobs: Job[] = [];
	let searchTerm = "";
	let selectedContract = "all";
	let isLoaded = false;

	const contractTypes = ["all", "CDI", "CDD", "Intérim", "Stage"];

	onMount(() => {
		const stored = sessionStorage.getItem("analysisResults");
		if (stored) {
			data = JSON.parse(stored);
			filteredJobs = data?.jobs || [];
			setTimeout(() => (isLoaded = true), 100);
		} else {
			goto("/");
		}
	});

	function filterJobs() {
		if (!data) return;
		const term = searchTerm.toLowerCase();
		filteredJobs = data.jobs.filter((job) => {
			const matchesSearch =
				job.intitule.toLowerCase().includes(term) ||
				job.entreprise.nom.toLowerCase().includes(term) ||
				job.lieuTravail.libelle.toLowerCase().includes(term);

			const matchesContract =
				selectedContract === "all" ||
				(job.contrat &&
					job.contrat
						.toLowerCase()
						.includes(selectedContract.toLowerCase()));

			return matchesSearch && matchesContract;
		});
	}

	function getExpBadge(level: string) {
		const map: Record<string, { label: string; color: string }> = {
			junior: { label: "Junior", color: "#10b981" },
			intermediaire: { label: "Intermédiaire", color: "#f59e0b" },
			senior: { label: "Senior", color: "#7c3aed" },
		};
		return map[level] || map.junior;
	}

	function getMatchColor(score?: number): string {
		if (!score) return "#4f46e5";
		if (score >= 80) return "#10b981";
		if (score >= 60) return "#f59e0b";
		return "#4f46e5";
	}

	function truncate(text: string, max: number): string {
		return text.length <= max ? text : text.slice(0, max).trim() + "...";
	}
</script>

<svelte:head>
	<title>Résultats - {data?.jobs.length || 0} offres | EasyJobFind</title>
</svelte:head>

{#if data}
	<div class="results-page" class:loaded={isLoaded}>
		<!-- Profile Section -->
		<section class="profile-section">
			<div class="container">
				<div class="profile-card card card-elevated">
					<div class="profile-header">
						<div>
							<span class="badge">Ton profil</span>
							<h1>{data.profile.metier_recherche}</h1>
						</div>
						<span
							class="exp-badge"
							style="background: {getExpBadge(
								data.profile.niveau_experience,
							).color}"
						>
							{getExpBadge(data.profile.niveau_experience).label}
						</span>
					</div>

					<div class="profile-grid">
						<div class="profile-box">
							<h3>💼 Compétences clés</h3>
							<div class="tags-wrap">
								{#each data.profile.competences_cles.slice(0, 8) as skill}
									<span class="tag">{skill}</span>
								{/each}
							</div>
						</div>

						<div class="profile-box">
							<h3>⭐ Points forts</h3>
							<div class="tags-wrap">
								{#each data.profile.points_forts.slice(0, 4) as point}
									<span class="tag tag-success">{point}</span>
								{/each}
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Jobs Section -->
		<section class="jobs-section">
			<div class="container">
				<div class="jobs-header">
					<div>
						<h2>🎉 {data.jobs.length} offres trouvées</h2>
						<p>Offres France Travail correspondant à ton profil</p>
					</div>
				</div>

				<!-- Filters -->
				<div class="filters">
					<div class="search-input">
						<svg
							width="18"
							height="18"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<circle cx="11" cy="11" r="8" />
							<path d="m21 21-4.35-4.35" />
						</svg>
						<input
							type="text"
							placeholder="Rechercher..."
							bind:value={searchTerm}
							oninput={filterJobs}
						/>
					</div>

					<div class="filter-pills">
						{#each contractTypes as type}
							<button
								class="pill"
								class:active={selectedContract === type}
								onclick={() => {
									selectedContract = type;
									filterJobs();
								}}
							>
								{type === "all" ? "Tous" : type}
							</button>
						{/each}
					</div>
				</div>

				<!-- Jobs Grid -->
				{#if filteredJobs.length > 0}
					<div class="jobs-grid">
						{#each filteredJobs as job, i}
							<article
								class="job-card card hover-lift"
								style="animation-delay: {Math.min(
									i * 0.05,
									0.4,
								)}s"
							>
								{#if job.matching_score}
									<div
										class="match-badge"
										style="background: {getMatchColor(
											job.matching_score,
										)}"
									>
										{job.matching_score}%
									</div>
								{/if}

								<div class="job-top">
									<h3>{truncate(job.intitule, 55)}</h3>
									{#if job.contrat}
										<span class="contract-pill"
											>{job.contrat}</span
										>
									{/if}
								</div>

								<div class="job-meta">
									<span class="meta-item">
										<svg
											width="14"
											height="14"
											viewBox="0 0 24 24"
											fill="none"
											stroke="currentColor"
											stroke-width="2"
										>
											<path
												d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"
											/>
										</svg>
										{job.entreprise.nom}
									</span>
									<span class="meta-item">
										<svg
											width="14"
											height="14"
											viewBox="0 0 24 24"
											fill="none"
											stroke="currentColor"
											stroke-width="2"
										>
											<path
												d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"
											/>
											<circle cx="12" cy="10" r="3" />
										</svg>
										{job.lieuTravail.libelle}
									</span>
									{#if job.salaire}
										<span class="meta-item salary">
											{job.salaire}
										</span>
									{/if}
								</div>

								<p class="job-desc">
									{truncate(job.description, 150)}
								</p>

								<a
									href={job.url}
									target="_blank"
									rel="noopener noreferrer"
									class="btn btn-success apply-btn"
									onclick={(e) => {
										// Fallback pour mobile si le target="_blank" est bloqué
										if (window.innerWidth < 768) {
											e.preventDefault();
											window.location.href = job.url;
										}
									}}
								>
									Voir l'offre sur France Travail
									<svg
										width="16"
										height="16"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
									>
										<path
											d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"
										/>
										<polyline points="15 3 21 3 21 9" />
										<line x1="10" y1="14" x2="21" y2="3" />
									</svg>
								</a>
							</article>
						{/each}
					</div>
				{:else}
					<div class="no-results card">
						<span class="no-icon">😕</span>
						<h3>Aucune offre trouvée</h3>
						<p>Essaie de modifier tes critères</p>
						<button
							class="btn btn-outline"
							onclick={() => {
								searchTerm = "";
								selectedContract = "all";
								filterJobs();
							}}
						>
							Réinitialiser
						</button>
					</div>
				{/if}

				<div class="actions">
					<a href="/" class="btn btn-outline">
						← Nouvelle recherche
					</a>
				</div>
			</div>
		</section>
	</div>
{:else}
	<div class="loading">
		<div class="spinner spinner-dark spinner-lg"></div>
		<p>Chargement...</p>
	</div>
{/if}

<style>
	.results-page {
		opacity: 0;
		transition: opacity 0.3s;
	}

	.results-page.loaded {
		opacity: 1;
	}

	/* Profile */
	.profile-section {
		padding: 2rem 0;
		background: var(--bg-secondary);
	}

	.profile-card {
		padding: 2rem;
	}

	.profile-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 1rem;
		margin-bottom: 2rem;
		padding-bottom: 1.5rem;
		border-bottom: 1px solid var(--border-light);
	}

	.profile-header h1 {
		font-size: 1.75rem;
		margin-top: 0.5rem;
	}

	.exp-badge {
		padding: 0.5rem 1rem;
		border-radius: var(--radius-full);
		color: white;
		font-size: 0.8125rem;
		font-weight: 600;
	}

	.profile-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
	}

	.profile-box h3 {
		font-size: 0.9375rem;
		margin-bottom: 0.75rem;
		color: var(--text-secondary);
	}

	.tags-wrap {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.tag-success {
		background: rgba(16, 185, 129, 0.1);
		color: var(--success);
		border-color: rgba(16, 185, 129, 0.2);
	}

	/* Jobs */
	.jobs-section {
		padding: 2rem 0 4rem;
	}

	.jobs-header {
		margin-bottom: 1.5rem;
	}

	.jobs-header h2 {
		font-size: 1.5rem;
		margin-bottom: 0.25rem;
	}

	.jobs-header p {
		color: var(--text-muted);
	}

	.filters {
		display: flex;
		gap: 1rem;
		margin-bottom: 2rem;
		flex-wrap: wrap;
	}

	.search-input {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.625rem 1rem;
		background: var(--bg-primary);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-lg);
		flex: 1;
		max-width: 320px;
	}

	.search-input svg {
		color: var(--text-muted);
	}

	.search-input input {
		flex: 1;
		border: none;
		background: none;
		font-size: 0.9375rem;
		color: var(--text-primary);
		outline: none;
	}

	.filter-pills {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.pill {
		padding: 0.5rem 1rem;
		border: 1px solid var(--border-light);
		border-radius: var(--radius-full);
		background: var(--bg-primary);
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--text-secondary);
		cursor: pointer;
		transition: all 0.2s;
	}

	.pill:hover {
		border-color: var(--primary);
		color: var(--primary);
	}

	.pill.active {
		background: var(--primary);
		border-color: var(--primary);
		color: white;
	}

	.jobs-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
		gap: 1.5rem;
	}

	.job-card {
		position: relative;
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		animation: fadeInUp 0.4s ease forwards;
		opacity: 0;
	}

	.match-badge {
		position: absolute;
		top: 1rem;
		right: 1rem;
		padding: 0.25rem 0.625rem;
		border-radius: var(--radius-full);
		font-size: 0.75rem;
		font-weight: 700;
		color: white;
	}

	.job-top {
		margin-bottom: 0.75rem;
		padding-right: 3rem;
	}

	.job-top h3 {
		font-size: 1.0625rem;
		line-height: 1.4;
		margin-bottom: 0.5rem;
	}

	.contract-pill {
		display: inline-block;
		padding: 0.25rem 0.5rem;
		background: rgba(79, 70, 229, 0.1);
		color: var(--primary);
		font-size: 0.6875rem;
		font-weight: 600;
		border-radius: 4px;
		text-transform: uppercase;
	}

	.job-meta {
		display: flex;
		flex-wrap: wrap;
		gap: 0.75rem;
		margin-bottom: 0.75rem;
	}

	.meta-item {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		font-size: 0.8125rem;
		color: var(--text-secondary);
	}

	.meta-item.salary {
		color: var(--success);
		font-weight: 500;
	}

	.job-desc {
		flex: 1;
		font-size: 0.875rem;
		color: var(--text-secondary);
		line-height: 1.6;
		margin-bottom: 1rem;
	}

	.apply-btn {
		margin-top: auto;
	}

	.no-results {
		text-align: center;
		padding: 4rem 2rem;
	}

	.no-icon {
		font-size: 3rem;
		display: block;
		margin-bottom: 1rem;
	}

	.no-results h3 {
		margin-bottom: 0.5rem;
	}

	.no-results p {
		margin-bottom: 1.5rem;
	}

	.actions {
		display: flex;
		justify-content: center;
		margin-top: 3rem;
	}

	.loading {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 60vh;
		gap: 1rem;
	}

	@keyframes fadeInUp {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@media (max-width: 768px) {
		.profile-grid {
			grid-template-columns: 1fr;
		}

		.jobs-grid {
			grid-template-columns: 1fr;
		}

		.filters {
			flex-direction: column;
		}

		.search-input {
			max-width: none;
		}
	}
</style>
