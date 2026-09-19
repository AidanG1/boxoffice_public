<script lang="ts">
	import { tmdb_path_to_url, type MovieData } from '$lib/utils'

	let {
		data
	}: {
		data: MovieData
	} = $props()
</script>

<h2 class="mb-2">Keywords</h2>
<div class="flex flex-wrap items-center gap-4">
	{#each data.movie.keywords || [] as keyword}
		<a href="/keyword/{keyword}">
			<div class="bg-base-200 flex items-center gap-2 rounded-md p-2">
				<span>{keyword}</span>
			</div>
		</a>
	{/each}
</div>
