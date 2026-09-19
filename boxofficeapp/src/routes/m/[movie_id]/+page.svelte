<script lang="ts">
	import MovieChart from '$lib/components/MovieChart.svelte'
	import WikipediaChart from '$lib/components/WikipediaChart.svelte'
	import { formatKMB, tmdb_path_to_url } from '$lib/utils'
	import DailyTable from './DailyTable.svelte'
	import CastCrew from './CastCrew.svelte'
	import Comps from './Comps.svelte'
	import PercentRanks from './PercentRanks.svelte'
	import Weekend from './Weekend.svelte'
	import Profitability from './Profitability.svelte'
	import ProductionCompanies from './ProductionCompanies.svelte'
	import { replaceState } from '$app/navigation'
	import Keywords from './Keywords.svelte'
	let { data } = $props()

	let movie_data = $state(data.movie)
	let movie = $state(data.movie.movie)

	type MovieRatings = {
		tmdb_rating: number
		imdb_rating: number
		metacritic_rating: number
		cinemascore: string | null
		popcorn_meter: number | null
		tomato_meter: number | null
		letterboxd_rating: number | null
	}

	type DataType = typeof data

	const getMovieRatings = (data: DataType): MovieRatings => {
		const mid = data.movie.movie_info_days || []
		if (mid.length === 0) {
			return {
				tmdb_rating: 0,
				imdb_rating: 0,
				metacritic_rating: 0,
				cinemascore: null,
				popcorn_meter: null,
				tomato_meter: null,
				letterboxd_rating: null
			}
		}

		const last_day = mid[mid.length - 1]
		return {
			tmdb_rating: Math.round(last_day.tmdb_vote_average * 10) / 10 || 0,
			imdb_rating: last_day.imdb_rating || 0,
			metacritic_rating: last_day.metacritic_rating || 0,
			cinemascore: movie.cinemascore || null,
			popcorn_meter: last_day.rt_popcorn_meter || null,
			tomato_meter: last_day.rt_tomato_meter || null,
			letterboxd_rating: Math.round(((last_day.letterboxd_average_rating || 0) / 100) * 100) / 100
		}
	}

	let movieRatings = $state(getMovieRatings(data))
	$effect(() => {
		movieRatings = getMovieRatings(data)
	})
</script>

<svelte:head>
	<title>{movie.title} - Reel Numbers</title>
	<meta
		name="description"
		content="Explore the box office performance of {movie.title} with detailed charts and statistics."
	/>
	<meta property="og:title" content="Reel Numbers - {movie.title}" />
	<meta
		property="og:description"
		content="Explore the box office performance of {movie.title} with detailed charts and statistics."
	/>
	<meta property="og:image" content={tmdb_path_to_url(movie.poster_path || '')} />
	<meta property="og:type" content="website" />
</svelte:head>
{#snippet logo_links(height_class: string = 'h-6')}
	<a href="https://www.themoviedb.org/movie/{movie.tmdb_id}" target="_blank">
		<img src="/logos/tmdb.svg" alt="TMDB" class={height_class} />
	</a>
	<a href="https://en.wikipedia.org/wiki/{movie.wikipedia_key}" target="_blank">
		<img src="/logos/wikipedia.svg" alt="Wikipedia" class={height_class} />
	</a>
	<a href="https://letterboxd.com/film/{movie.letterboxd_id}" target="_blank">
		<img src="/logos/letterboxd.svg" alt="Letterboxd" class={height_class} />
	</a>
	<a href="https://www.rottentomatoes.com/m/{movie.rotten_tomatoes_id}" target="_blank">
		<img src="/logos/rottentomatoes.svg" alt="Rotten Tomatoes" class={height_class} />
	</a>
	<a href={movie.homepage} target="_blank">
		<img src="/logos/website.svg" alt="Website" class={height_class} />
	</a>
	<a href="https://www.imdb.com/title/{movie.imdb_id}" target="_blank">
		<img src="/logos/imdb.svg" alt="IMDB" class={height_class} />
	</a>
	<a href="https://www.the-numbers.com/movie/{movie.numbers_slug}" target="_blank">
		<img src="/logos/numbers.svg" alt="Numbers" class={height_class} />
	</a>
	<a href="https://www.boxofficemojo.com/title/{movie.imdb_id}" target="_blank">
		<img src="/logos/boxofficemojo.svg" alt="Box Office Mojo" class={height_class} />
	</a>
{/snippet}

{#snippet title_with_release_date()}
	<div class="mt-4 md:mt-8">
		<span class="text-3xl font-bold md:text-4xl lg:text-6xl">
			{movie.title}
		</span>
		<span class="text-xl md:text-2xl lg:text-4xl"> ({movie.release_date.slice(0, 4)})</span>
	</div>
{/snippet}

{#snippet movie_poster(div_classes = '')}
	<div class="p-2 {div_classes}">
		<picture>
			<source
				srcset={tmdb_path_to_url(movie.poster_path || '', 'w1280')}
				media="(min-width: 640px)"
			/>
			<source
				srcset={tmdb_path_to_url(movie.poster_path || '', 'w500')}
				media="(max-width: 639px)"
			/>
			<img
				src={tmdb_path_to_url(movie.poster_path || '')}
				alt="{movie.title} Poster"
				class="h-fit rounded-lg shadow-lg"
			/>
		</picture>
	</div>
{/snippet}

<div class="min-h-screen">
	<div
		class="w-fit bg-cover bg-center"
		style="background: linear-gradient(color-mix(in srgb, var(--color-base-100), rgba(0, 0, 0, 0.5) 50%), color-mix(in srgb, var(--color-base-100), rgba(0, 0, 0, 0.5) 50%)), url({tmdb_path_to_url(
			movie.backdrop_path || ''
		)})"
	>
		<div class="hidden md:flex">
			{@render movie_poster('md:w-1/3 lg:w-1/4')}

			<!-- details -->
			<div class="mb-2 grow pr-2">
				{@render title_with_release_date()}
				<!-- next links: TMDB, Numbers, Wikipedia, IMDB -->
				{#await data.prediction}
					<p>Loading prediction data...</p>
				{:then prediction}
					<div class="">
						<MovieChart {movie_data} prediction_data={prediction} />
					</div>
				{/await}
			</div>

			<!-- links to TMDB, Numbers, Wikipedia, IMDB -->
			<div class="absolute right-0 mt-1 flex gap-1">
				{@render logo_links()}
			</div>
		</div>
		<div class="block md:hidden">
			<div class="flex">
				{@render movie_poster('w-[40%]')}
				<div class="flex w-[60%] flex-col">
					<div class="grow">
						{@render title_with_release_date()}
					</div>
					<div class="mt-2 grid grid-flow-col grid-rows-2 gap-x-24">
						{@render logo_links()}
					</div>
				</div>
			</div>

			<div class="p-2">
				<MovieChart {movie_data} prediction_data={data.prediction} />
			</div>
		</div>
	</div>

	{#snippet movie_badges()}
		<div class="flex flex-col gap-2 md:flex-row">
			<div class="flex gap-2">
				{#each movie.movie_spoken_language as sl}
					<a href="/language/{sl.spoken_language.name}">
						<span class="badge badge-accent h-fit">{sl.spoken_language.name}</span>
					</a>
				{/each}
				{#each movie.movie_genre as mg}
					<a href="/tmdb_genre/{mg.genre.name}">
						<span class="badge badge-secondary h-fit">{mg.genre.name}</span>
					</a>
				{/each}
			</div>
			<div class="flex gap-2">
				<a href="/mpaa/{movie.mpaa_rating}">
					<span class="badge badge-info h-fit">{movie.mpaa_rating}</span>
				</a>
				<a href="/creative/{movie.creative_type}">
					<span class="badge badge-primary h-fit">{movie.creative_type}</span>
				</a>
				<a href="/production_method/{movie.production_method.replace('/', '-')}">
					<span class="badge badge-primary h-fit">{movie.production_method}</span>
				</a>
				<a href="/source/{movie.source.replace('/', '-')}">
					<span class="badge badge-primary h-fit">{movie.source}</span>
				</a>
			</div>
		</div>
	{/snippet}

	<!-- Info about movie -->
	<div class="p-4">
		<div class="mb-2 flex flex-col gap-2 md:flex-row">
			<h2 class="grow text-3xl font-bold">Movie Information</h2>
			{@render movie_badges()}
		</div>
		<div class="flex">
			<div class="mr-2 w-1/3">
				<p class="mb-1">
					<a
						href={`/day/${
							movie_data.boxofficedays.filter((bod) => bod.is_new_release)[0]?.date ||
							movie.release_date
						}`}
					>
						<strong>Release Date:</strong>
						{movie_data.boxofficedays.filter((bod) => bod.is_new_release)[0]?.date ||
							movie.release_date}
					</a>
				</p>
				<p class="mb-1">
					<a href="/budget/{movie.budget}">
						<strong>Budget:</strong>
						{formatKMB(movie.budget || 0)}
					</a>
				</p>
				<p class="mb-1">
					<a href="/runtime/{movie.runtime}">
						<strong>Runtime:</strong>
						{movie.runtime}
					</a>
				</p>
				{#if movie.cinemascore}
					<p class="mb-1">
						<a href="/cinemascore/{movie.cinemascore}">
							<strong>Cinemascore:</strong>
							{movie.cinemascore}
						</a>
					</p>
				{/if}
			</div>
			<div>
				<p>
					<strong>Domestic Total</strong>: {formatKMB(data.screener.domestic_revenue || 0, 2)}
				</p>
				<p>
					<strong>Opening Weekend</strong>: {formatKMB(
						data.screener.opening_weekend_revenue || 0,
						2
					)}
				</p>
				<p>
					<strong>Legs</strong>: {(data.screener.legs || 0).toFixed(2)}
				</p>
				<p>
					<strong>Overview:</strong>
					{movie.overview || 'No overview available for this movie.'}
				</p>
			</div>
		</div>
		<hr />
		{#snippet radial(
			title: string,
			value_show: number,
			value_dial: number,
			fixed_value: number = 1
		)}
			<div class="flex flex-col items-center gap-2">
				<h3 class="text-center text-lg font-semibold">{title}</h3>
				<div
					class="radial-progress text-lg font-semibold {value_dial >= 75
						? 'text-success'
						: value_dial >= 60
						? 'text-warning'
						: 'text-error'}"
					style="--value:{value_dial};"
					role="progressbar"
					aria-label="Dial showing {title}"
					aria-valuenow={value_dial}
				>
					{value_show.toFixed(fixed_value)}
				</div>
			</div>
		{/snippet}
		<!-- Ratings from different sources, tmdb, imdb, and metacritic -->
		<div class="mb-2 flex flex-col gap-4 md:flex-row">
			<div class="grid grid-cols-3 place-items-center gap-4 md:w-1/2">
				{@render radial('TMDB', movieRatings.tmdb_rating, movieRatings.tmdb_rating * 10, 1)}
				{@render radial('IMDB', movieRatings.imdb_rating / 10, movieRatings.imdb_rating, 1)}
				{@render radial(
					'Metacritic',
					movieRatings.metacritic_rating,
					movieRatings.metacritic_rating,
					0
				)}
				{#if movieRatings.tomato_meter}
					{@render radial('RT Tomato', movieRatings.tomato_meter, movieRatings.tomato_meter, 0)}
				{/if}
				{#if movieRatings.popcorn_meter}
					{@render radial('RT Popcorn', movieRatings.popcorn_meter, movieRatings.popcorn_meter, 0)}
				{/if}
				{#if movieRatings.letterboxd_rating}
					{@render radial(
						'Letterboxd',
						movieRatings.letterboxd_rating,
						movieRatings.letterboxd_rating * 20,
						2
					)}
				{/if}
			</div>
			<div class="h-max md:w-1/2">
				<WikipediaChart {movie_data} />
			</div>
		</div>

		<hr />

		<!-- name of each tab group should be unique -->
		<div class="tabs tabs-border">
			<input type="radio" name="tabs_1" class="tab" aria-label="Dailies" checked />
			<div class="tab-content border-base-300 p-2 md:p-6">
				<DailyTable data={movie_data} />
			</div>

			<input type="radio" name="tabs_1" class="tab" aria-label="Weekends" />
			<div class="tab-content border-base-300 p-2 md:p-6">
				<Weekend movie_id={movie.id} />
			</div>

			<input type="radio" name="tabs_1" class="tab" aria-label="Cast and Crew" />
			<div class="tab-content border-base-300 p-2 md:p-6">
				<CastCrew data={movie_data} />
			</div>

			<input type="radio" name="tabs_1" class="tab" aria-label="Comps" />
			<div class="tab-content border-base-300 p-2 md:p-6">
				<Comps data={movie_data} />
			</div>

			<input type="radio" name="tabs_1" class="tab" aria-label="Percent Ranks" />
			<div class="tab-content border-base-300 p-2 md:p-6">
				<PercentRanks movie_id={movie.id} />
			</div>

			<input type="radio" name="tabs_1" class="tab" aria-label="Profitability" />
			<div class="tab-content border-base-300 p-2 md:p-6">
				<Profitability data={movie_data} screener_data={data.screener} />
			</div>

			<input type="radio" name="tabs_1" class="tab" aria-label="Production Companies" />
			<div class="tab-content border-base-300 p-2 md:p-6">
				<ProductionCompanies data={movie_data} />
			</div>

			<input type="radio" name="tabs_1" class="tab" aria-label="Keywords" />
			<div class="tab-content border-base-300 p-2 md:p-6">
				<Keywords data={movie_data} />
			</div>
		</div>
	</div>
</div>
