<script lang="ts">
	import { formatKMB } from '$lib/utils.js'

	let { data } = $props()
</script>

<svelte:head>
	<title>Reel Numbers - {data.category} '{data.value}'</title>
	<meta name="description" content={`Box office data for ${data.title}`} />
</svelte:head>

<div class="p-2">
	<div class="flex items-center gap-2 mb-4">
		<h1 class="grow">{data.title}</h1>

		{#if data.b64}
			<p>
				<a href={`/screen?b64=${data.b64}`} class="btn btn-primary"> View in Screener </a>
			</p>
		{/if}
	</div>

	<table class="table">
		<thead>
			<tr>
				<th>Rank</th>
				<th>Title</th>
				<th>Release Date</th>
				<th>Budget</th>
				<th>Domestic Revenue</th>
				<th>Revenue / Budget</th>
			</tr>
		</thead>
		<tbody>
			{#each data.movies as movie, index}
				<tr>
					<td>{index + 1}</td>
					<td><a href={`/m/${movie.return_id}`}>{movie.title}</a></td>
					<td>{movie.release_date}</td>
					<td>${formatKMB(movie.budget)}</td>
					<td>${formatKMB(movie.total_revenue, 2)}</td>
					<td>
						{movie.budget === 0 ? 'N/A' : (movie.total_revenue / movie.budget).toFixed(2)}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
