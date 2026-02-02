<script lang="ts">
	import "../app.css";

	let { children } = $props();
</script>

<div class="app">
	<header>
		<nav class="container">
			<a href="/" class="logo">
				<div class="logo-icon">
					<svg width="32" height="32" viewBox="0 0 32 32" fill="none">
						<rect
							width="32"
							height="32"
							rx="8"
							fill="url(#logo-gradient)"
						/>
						<path
							d="M9 16L14 21L23 11"
							stroke="white"
							stroke-width="3"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
						<defs>
							<linearGradient
								id="logo-gradient"
								x1="0"
								y1="0"
								x2="32"
								y2="32"
							>
								<stop stop-color="#4f46e5" />
								<stop offset="1" stop-color="#7c3aed" />
							</linearGradient>
						</defs>
					</svg>
				</div>
				<span class="logo-text">EasyJobFind</span>
			</a>
			<div class="nav-links">
				<a href="/" class="nav-link">Accueil</a>
				<a href="/about" class="nav-link">Comment ça marche</a>
			</div>
			<a href="/" class="btn btn-primary btn-sm nav-cta">
				Analyser mon CV
				<svg
					width="16"
					height="16"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
				>
					<path d="M5 12h14m-7-7l7 7-7 7" />
				</svg>
			</a>
		</nav>
	</header>

	<main>
		{@render children()}
	</main>

	<footer>
		<div class="container">
			<div class="footer-content">
				<div class="footer-brand">
					<div class="footer-logo">
						<svg
							width="28"
							height="28"
							viewBox="0 0 32 32"
							fill="none"
						>
							<rect
								width="32"
								height="32"
								rx="8"
								fill="url(#footer-gradient)"
							/>
							<path
								d="M9 16L14 21L23 11"
								stroke="white"
								stroke-width="3"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
							<defs>
								<linearGradient
									id="footer-gradient"
									x1="0"
									y1="0"
									x2="32"
									y2="32"
								>
									<stop stop-color="#4f46e5" />
									<stop offset="1" stop-color="#7c3aed" />
								</linearGradient>
							</defs>
						</svg>
						<span>EasyJobFind</span>
					</div>
					<p>
						Trouve ton emploi idéal grâce à l'intelligence
						artificielle et aux offres France Travail.
					</p>
				</div>
				<div class="footer-links">
					<div class="footer-col">
						<h4>Produit</h4>
						<a href="/">Trouver un emploi</a>
						<a href="/about">Comment ça marche</a>
					</div>
					<div class="footer-col">
						<h4>Partenaires</h4>
						<a
							href="https://francetravail.fr"
							target="_blank"
							rel="noopener">France Travail</a
						>
						<a
							href="https://groq.com"
							target="_blank"
							rel="noopener">Groq AI</a
						>
					</div>
				</div>
			</div>
			<div class="footer-bottom">
				<p>
					© 2025 EasyJobFind. Propulsé par <strong>Groq AI</strong> &
					<strong>France Travail</strong>
				</p>
			</div>
		</div>
	</footer>
</div>

<style>
	.app {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		background: var(--bg-secondary);
	}

	/* ===================================================
	   Header Premium
	   =================================================== */
	header {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 1000;
		background: rgba(255, 255, 255, 0.95);
		backdrop-filter: blur(20px);
		border-bottom: 1px solid var(--border-light);
	}

	nav {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.875rem 0;
		gap: 2rem;
	}

	.logo {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		text-decoration: none;
		transition: opacity 0.2s;
	}

	.logo:hover {
		opacity: 0.8;
	}

	.logo-icon {
		display: flex;
		flex-shrink: 0;
	}

	.logo-text {
		font-size: 1.25rem;
		font-weight: 800;
		color: var(--text-primary);
		letter-spacing: -0.02em;
	}

	.nav-links {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-right: auto;
	}

	.nav-link {
		padding: 0.5rem 1rem;
		font-size: 0.9375rem;
		font-weight: 500;
		color: var(--text-secondary);
		border-radius: var(--radius-md);
		transition: all 0.2s;
	}

	.nav-link:hover {
		color: var(--text-primary);
		background: var(--bg-tertiary);
	}

	.nav-cta {
		display: flex;
		gap: 0.5rem;
	}

	/* ===================================================
	   Main
	   =================================================== */
	main {
		flex: 1;
		padding-top: 64px;
	}

	/* ===================================================
	   Footer Premium
	   =================================================== */
	footer {
		background: var(--bg-primary);
		border-top: 1px solid var(--border-light);
		padding: 4rem 0 2rem;
		margin-top: auto;
	}

	.footer-content {
		display: grid;
		grid-template-columns: 1.5fr 1fr;
		gap: 4rem;
		margin-bottom: 3rem;
	}

	.footer-brand {
		max-width: 320px;
	}

	.footer-logo {
		display: flex;
		align-items: center;
		gap: 0.625rem;
		margin-bottom: 1rem;
	}

	.footer-logo span {
		font-size: 1.125rem;
		font-weight: 700;
		color: var(--text-primary);
	}

	.footer-brand p {
		font-size: 0.9375rem;
		color: var(--text-muted);
		line-height: 1.6;
	}

	.footer-links {
		display: flex;
		gap: 4rem;
	}

	.footer-col h4 {
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		margin-bottom: 1rem;
	}

	.footer-col a {
		display: block;
		font-size: 0.9375rem;
		color: var(--text-secondary);
		padding: 0.375rem 0;
		transition: color 0.2s;
	}

	.footer-col a:hover {
		color: var(--primary);
	}

	.footer-bottom {
		padding-top: 2rem;
		border-top: 1px solid var(--border-light);
	}

	.footer-bottom p {
		font-size: 0.875rem;
		color: var(--text-muted);
		text-align: center;
	}

	.footer-bottom strong {
		color: var(--primary);
	}

	/* ===================================================
	   Responsive
	   =================================================== */
	@media (max-width: 768px) {
		.nav-links {
			display: none;
		}

		.footer-content {
			grid-template-columns: 1fr;
			gap: 2rem;
		}

		.footer-links {
			gap: 2rem;
		}
	}
</style>
