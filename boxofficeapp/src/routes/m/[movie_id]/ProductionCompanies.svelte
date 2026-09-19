<script lang="ts">
	import { tmdb_path_to_url, type MovieData } from '$lib/utils'

	let {
		data
	}: {
		data: MovieData
	} = $props()
</script>

<h2 class="mb-2">Production Companies</h2>
<div class="flex flex-wrap items-center gap-4">
	{#each data.movie.movie_production_company as { production_company }}
		<a href="/company/{production_company.name}">
			<div class="bg-base-200 flex items-center gap-2 rounded-md p-2">
				{#if production_company.logo_path}
					<img
						src={tmdb_path_to_url(production_company.logo_path, 'w185')}
						alt={`${production_company.name} logo`}
						class="h-24 max-w-[100px] object-contain"
					/>
				{:else}
					<span>{production_company.name}</span>
				{/if}
			</div>
		</a>
	{/each}
</div>
