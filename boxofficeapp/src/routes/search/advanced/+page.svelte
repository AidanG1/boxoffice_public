<script lang="ts">
	import { multiSearch, type MultiSearchResult } from '$lib/utils'

	let searchQuery = $state('')
	let loading = $state(false)
	let searchResults: MultiSearchResult = $state({
		movies: [],
		people: [],
		companies: []
	})

	const handleSearch = async () => {
		loading = true
		searchResults = await multiSearch(searchQuery)
		loading = false
	}
</script>

<div class="p-2">
	<h1>Advanced Search</h1>

	<form onsubmit={handleSearch} class="flex w-full justify-center gap-2 p-4">
		<input type="text" placeholder="Search..." class="input" bind:value={searchQuery} />
		<button class="btn btn-primary" type="submit">Search</button>
	</form>

	<div class="p-4">
		<h2>Results</h2>

		{#if loading}
			<span class="loading loading-spinner loading-lg"></span>
		{:else if searchResults}
			<div class="flex gap-2 w-full justify-around">
				<div>
					<h3>Movies</h3>
					<ul>
						{#each searchResults.movies as movie}
							<li><a href={`/m/${movie.id}`}>{movie.title} ({movie.release_date?.slice(0, 4)})</a></li>
						{/each}
					</ul>
				</div>

				<div>
					<h3>People</h3>
					<ul>
						{#each searchResults.people as person}
							<li><a href={`/p/${person.id}`}>{person.name}</a></li>
						{/each}
					</ul>
				</div>

				<div>
					<h3>Companies</h3>
					<ul>
						{#each searchResults.companies as company}
							<li><a href={`/company/${company.name}`}>{company.name}</a></li>
						{/each}
					</ul>
				</div>
			</div>
		{:else}
			<p>No results found.</p>
		{/if}
	</div>
</div>
