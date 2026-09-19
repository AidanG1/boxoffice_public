<script lang="ts">
	import type { ScreenResult } from '$lib/screener'
	import { formatKMB } from '$lib/utils'
	import type { FilterSort } from './filterSort.svelte'
	import ScreenerImage from './ScreenerImage.svelte'

	let {
		filterSort,
		results
	}: {
		filterSort: FilterSort
		results: ScreenResult | null
	} = $props()

	let imageTitle: string = $state('My Screener')
	let imageMovieCount: number = $state(10)
</script>

<form class="flex flex-col gap-2">
	<label class="form-control w-full max-w-xs">
		<div class="label">
			<span class="label-text">Title</span>
		</div>
		<input
			type="text"
			placeholder="Enter title"
			class="input input-bordered w-full max-w-xs"
			bind:value={imageTitle}
		/>
		<button
			class="btn btn-success mt-1"
			onclick={async () => {
				const prompt = `Generate a title for a chart with the following information in it: Sort: ${filterSort.sort.name} ${filterSort.sort.direction}. Chart Columns: ${filterSort.filters.map((c) => `${c.name} ${c.type} ${c.value}`).join(', ')}. Do not include "Title:" at the beginning`;
				console.log(prompt);
			}}
		>
			Generate Image Title
		</button>
	</label>
	<label class="form-control w-full max-w-xs">
		<div class="label">
			<span class="label-text">Movie Count</span>
		</div>
		<input
			type="number"
			placeholder="Movie Count"
			class="input input-bordered w-full max-w-xs"
			bind:value={imageMovieCount}
		/>
	</label>

	<ScreenerImage
		movies={results?.screener_view
			.map((movie) => ({
				title: movie.title,
				poster_path: movie.poster_path,
				stat: `$${formatKMB(movie.domestic_revenue, 2)}`
			}))
			.slice(0, imageMovieCount) ?? []}
		title={imageTitle}
	/>
</form>
