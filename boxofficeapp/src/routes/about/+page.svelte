<script>
	import SimpleMovieChart from '$lib/components/SimpleMovieChart.svelte'
	import WikipediaChart from '$lib/components/WikipediaChart.svelte'

	// Placeholder data for charts and testimonials
	const features = [
		{ icon: '📈', title: 'Hourly Data Updates', desc: 'Stay ahead with consistent new data.' },
		{
			icon: '📊',
			title: 'Advanced Analytics',
			desc: 'Unlock trends and predictive insights with powerful analytics.'
		},
		{
			icon: '🛠️',
			title: 'Customizable Exports',
			desc: 'Export the data you need, how you need it.'
		}
		// { icon: '🔔', title: 'Alerts & Notifications', desc: 'Get notified about key market shifts and opportunities.' }
	]
	const testimonials = [
		{
			name: 'Jake G.',
			role: 'Investor',
			quote:
				'BoxOffice Insights helped me optimize my prediction market strategies and boost returns.'
		},
		{
			name: 'Tyler D.',
			role: 'Prediction Market Investor',
			quote: 'The predictive analytics are a game-changer for my investment approach.'
		}
	]
	const partners = [
		'logos/imdb.svg',
		'logos/numbers.svg',
		'logos/letterboxd.svg',
		'logos/tmdb.svg'
	]

	let { data } = $props()
</script>

<svelte:head>
	<title>BoxOffice Insights</title>
	<meta name="description" content="Unlock box office insights with advanced analytics and data." />
	<meta property="og:title" content="BoxOffice Insights" />
	<meta property="og:description" content="Advanced box office analytics for prediction markets." />
	<meta property="og:image" content="/filmreel.svg" />
	<meta property="og:type" content="website" />
</svelte:head>

<div class="posters-bg">
	<div class="posters-grid">
		<img
			src="https://www.themoviedb.org/t/p/w1280/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg"
			alt="Star Wars"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg"
			alt="Titanic"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/an0nD6uq6byfxXCfk6lQBzdL2J1.jpg"
			alt="ET the Extra-Terrestrial"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/wqnLdwVXoBjKibFRR5U3y0aDUhs.jpg"
			alt="Star Wars: The Force Awakens"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/kyeqWdyUXW608qlYkRqosgbbJyK.jpg"
			alt="Avatar"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/nNAeTmF4CtdSgMDplXTDPOpYzsX.jpg"
			alt="The Empire Strikes Back"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/ulzhLuWrPK07P1YkdWQLZnQh1JL.jpg"
			alt="Avengers: Endgame"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/jQYlydvHm3kUix1f8prMucrplhm.jpg"
			alt="Return of the Jedi"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/63viWuPfYQjRYLSZSZNq7dglJP5.jpg"
			alt="Jurassic Park"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/6wkfovpn7Eq8dYNKaG5PY3q2oq6.jpg"
			alt="The Phantom Menace"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/sKCr78MXSLixwmZ8DyJLrpMsd15.jpg"
			alt="The Lion King"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg"
			alt="Forrest Gump"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/ceG9VzoRAVGwivFU403Wc3AHRys.jpg"
			alt="Raiders of the Lost Ark"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg"
			alt="Spider-Man: No Way Home"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg"
			alt="The Avengers"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/rhr4y79GpxQF9IsfJItRXVaoGs4.jpg"
			alt="Jurassic World"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/uxzzxijgPIY7slzFvMotPv8wjKA.jpg"
			alt="Black Panther"
			class="poster-img"
		/>
		<img
			src="https://www.themoviedb.org/t/p/w1280/yaPx3cK9zGFX3SbcKwxWM1QIbUh.jpg"
			alt="Close Encounters of the Third Kind"
			class="poster-img"
		/>
	</div>
</div>

<!-- Hero Section -->
<div class="relative flex flex-col items-center bg-cover bg-center px-4 py-24 text-center">
	<div
		class="inline-block max-w-2xl rounded-2xl border border-yellow-400/20 bg-black/70 px-8 py-10 shadow-2xl backdrop-blur-md"
	>
		<h1
			class="mb-4 text-4xl font-extrabold tracking-tight text-yellow-400 drop-shadow-lg md:text-5xl"
		>
			Unlock Box Office Insights
		</h1>
		<p class="mb-4 text-lg leading-relaxed font-medium text-gray-100 md:text-xl">
			Data-driven insights for investors in prediction markets.<br />
			Maximize your returns and optimize your strategy with SOTA box office analytics.
		</p>
		<div class="mb-8">
			<span class="mb-1 block text-base font-semibold text-yellow-300 md:text-lg"
				>Powered by <span class="font-bold text-white">complete box office data</span> and trusted sources:</span
			>
			<span class="mt-1 flex flex-wrap justify-center gap-2">
				<span class="rounded bg-yellow-400/20 px-2 py-0.5 font-bold text-white">IMDb</span>
				<span class="rounded bg-yellow-400/20 px-2 py-0.5 font-bold text-white">TMDb</span>
				<span class="rounded bg-yellow-400/20 px-2 py-0.5 font-bold text-white"
					>Rotten Tomatoes</span
				>
				<span class="rounded bg-yellow-400/20 px-2 py-0.5 font-bold text-white">Letterboxd</span>
				<span class="rounded bg-yellow-400/20 px-2 py-0.5 font-bold text-white">The Numbers</span>
				<span class="rounded bg-yellow-400/20 px-2 py-0.5 font-bold text-white">Wikipedia</span>
			</span>
		</div>
		<a href="/recent">
			<button
				class="rounded-full bg-yellow-400 px-8 py-3 font-bold text-[#181a20] shadow-lg transition hover:bg-yellow-300"
			>
				Get Started
			</button>
		</a>
	</div>
</div>

<!-- Data Showcase -->
<section
	class="relative z-10 mx-auto -mt-12 flex max-w-5xl flex-wrap items-stretch justify-center gap-8 rounded-2xl bg-black/70 px-4 py-14 shadow-xl"
>
	<div
		class="flex max-w-md min-w-[320px] flex-1 flex-col items-center rounded-2xl border border-yellow-400/10 bg-gradient-to-br from-[#23242a] to-[#181a20] p-8 shadow-lg"
	>
		<div class="w-80">
			<SimpleMovieChart
				movie_data={data.movie_data}
				text_color="#ffffff"
				line_color="#fcc800"
				movie_title_in_title={true}
			/>
		</div>
	</div>
	<div
		class="flex max-w-md min-w-[320px] flex-1 flex-col items-center rounded-2xl border border-blue-400/10 bg-gradient-to-br from-[#23242a] to-[#181a20] p-8 shadow-lg"
	>
		<div class="h-56 w-80">
			<WikipediaChart
				movie_data={data.movie_data}
				text_color="#ffffff"
				line_color="#fcc800"
				base_color="#23242a"
				movie_title_in_title={true}
			/>
		</div>
	</div>
</section>

<!-- Comps & Investors Section Combined -->
<section class="mx-auto my-16 flex max-w-5xl flex-wrap justify-center gap-8">
	<div
		class="flex max-w-3xl min-w-[320px] flex-1 flex-col items-stretch rounded-2xl border border-yellow-400/10 bg-gradient-to-br from-[#23242a] to-[#181a20] p-10 shadow-xl md:flex-row"
	>
		<div
			class="mb-8 flex flex-1 flex-col items-center justify-center text-center md:mr-8 md:mb-0 md:items-start md:text-left"
		>
			<h2 class="mb-4 text-3xl font-extrabold tracking-tight text-yellow-400 md:text-4xl">
				State-of-the-Art & Customizable Comps
			</h2>
			<p class="mb-6 max-w-xl text-lg text-gray-200 md:text-xl">
				Instantly compare any movie to a curated set of historical and current comps using advanced,
				interactive visualizations.<br class="hidden md:inline" /> Tailor your comp set by genre, release
				window, distributor, and more—giving you the edge in prediction markets.
			</p>
			<div class="mb-2 flex flex-wrap justify-center gap-4 md:justify-start">
				<span
					class="rounded-full bg-yellow-400/20 px-4 py-2 text-base font-semibold text-yellow-300 shadow"
					>Custom Filters</span
				>
				<span
					class="rounded-full bg-yellow-400/20 px-4 py-2 text-base font-semibold text-yellow-300 shadow"
					>Interactive Charts</span
				>
				<span
					class="rounded-full bg-yellow-400/20 px-4 py-2 text-base font-semibold text-yellow-300 shadow"
					>Hourly Updates</span
				>
				<span
					class="rounded-full bg-yellow-400/20 px-4 py-2 text-base font-semibold text-yellow-300 shadow"
					>Exportable Data</span
				>
			</div>
		</div>
		<div
			class="flex flex-1 flex-col items-center justify-center rounded-2xl border border-yellow-400/10 bg-[#23242a] p-8 shadow-inner md:items-start"
		>
			<h3 class="mb-2 text-2xl font-bold tracking-tight text-yellow-400 md:text-3xl">
				For Investors in Prediction Markets
			</h3>
			<p class="mb-6 text-lg text-gray-200">
				Leverage predictive analytics and hourly-updated data to make smarter investments on box
				office outcomes. Access exclusive trends and actionable insights.
			</p>
			<p class="mt-2 mb-6 block font-semibold text-yellow-300">
				Our data sources include <span class="text-white">IMDb</span>,
				<span class="text-white">TMDb</span>, <span class="text-white">Rotten Tomatoes</span>,
				<span class="text-white">Letterboxd</span>, <span class="text-white">The Numbers</span>,
				<span class="text-white">Wikipedia</span>, and complete box office data.
			</p>
			<button
				class="rounded-full bg-yellow-400 px-6 py-2 font-semibold text-[#181a20] shadow transition hover:bg-yellow-300"
				>See Data for Investors</button
			>
		</div>
	</div>
</section>

<!-- Features and Benefits -->
<section class="my-12 flex flex-wrap justify-center gap-8">
	{#each features as f}
		<div
			class="flex max-w-xs min-w-[180px] flex-1 flex-col items-center rounded-xl bg-[#23242a] p-6 shadow"
		>
			<div class="mb-2 text-3xl">{f.icon}</div>
			<div class="mb-1 font-bold text-yellow-400">{f.title}</div>
			<div class="text-center text-base text-gray-400">{f.desc}</div>
		</div>
	{/each}
</section>

<!-- Testimonials -->
<section
	class="mx-auto my-12 flex max-w-3xl flex-wrap justify-center gap-8 rounded-xl bg-[#1e1f25] p-10 shadow"
>
	{#each testimonials as t}
		<div
			class="max-w-md min-w-[220px] flex-1 rounded-lg bg-[#23242a] p-6 text-gray-200 italic shadow"
		>
			“{t.quote}”
			<div class="mt-4 font-bold text-yellow-400 not-italic">— {t.name}, {t.role}</div>
		</div>
	{/each}
</section>

<!-- Partners -->
<div class="my-8 flex items-center justify-center gap-8">
	{#each partners as logo}
		<img
			src={logo}
			alt="Partner logo"
			class="h-9 opacity-80 grayscale transition hover:opacity-100 hover:grayscale-0"
		/>
	{/each}
</div>

<!-- Footer -->
<footer class="border-t border-[#23242a] bg-[#181a20] py-8 text-center text-base text-gray-400">
	<nav class="mb-2">
		<a href="/about" class="mx-3 font-semibold text-yellow-400 transition hover:text-yellow-300"
			>About</a
		>
	</nav>
	<div class="mt-2">&copy; {new Date().getFullYear()} Reel Numbers. All rights reserved.</div>
</footer>

<!-- Add a visually interesting background with movie posters -->
<style>
	.posters-bg {
		position: fixed;
		inset: 0;
		z-index: 0;
		pointer-events: none;
		opacity: 0.13;
		display: flex;
		justify-content: center;
		align-items: center;
		background:
			repeating-linear-gradient(135deg, #23242a 0 2px, transparent 2px 40px),
			repeating-linear-gradient(-135deg, #23242a 0 2px, transparent 2px 40px);
	}
	.posters-grid {
		display: grid;
		grid-template-columns: repeat(6, 1fr);
		grid-template-rows: repeat(2, 180px);
		gap: 20px;
		width: 100vw;
		margin: 40px auto 0 auto;
		pointer-events: none;
		justify-items: center;
		align-items: center;
	}
	.poster-img {
		width: 120px;
		height: 180px;
		object-fit: cover;
		border-radius: 0.5rem;
		box-shadow: 0 4px 24px 0 #0006;
		opacity: 0.85;
		filter: grayscale(0.2) blur(0.5px) brightness(1.1);
		transition: opacity 0.3s;
	}
	@media (max-width: 900px) {
		.posters-grid {
			grid-template-columns: repeat(3, 1fr);
			grid-template-rows: repeat(4, 120px);
			gap: 16px;
		}
		.poster-img {
			width: 80px;
			height: 120px;
		}
	}
</style>
