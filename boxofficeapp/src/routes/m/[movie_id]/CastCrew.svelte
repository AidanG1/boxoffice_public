<script lang="ts">
	import { type MovieData } from '$lib/utils'

	let {
		data,
	}: {
		data: MovieData
	} = $props()

	const order_cast_crew = (order_1: number | null, order_2: number | null) => {
		if (order_1 === null && order_2 === null) return 0
		if (order_1 === null) return 1
		if (order_2 === null) return -1
		return order_1 - order_2
	}

	// job importance order
	const jobImportance = [
		'Director',
		'Original Music Composer',
		'Director of Photography',
		'Writer',
		'Story',
		'Screenplay',
		'Producer',
		'Book',
		'Novel',
		'Characters',
		'Editor'
	]
</script>

<div class="grid md:gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
	<!-- just the crew up here -->
	{#each data.movie.castorcrew
		.filter((mcoc) => !mcoc.is_cast)
		.sort((a, b) => {
			const jobA = jobImportance.indexOf(a.job || '')
			const jobB = jobImportance.indexOf(b.job || '')
			return jobA - jobB
		}) as mcoc}
		<div class="border-b p-2 md:p-4 border-base-300">
			<a href="/p/{mcoc.person.id}">
				<h3 class="md:text-lg font-semibold">
					{mcoc.person.name}
				</h3>
				<p class="text-sm">{mcoc.job || 'N/A'}</p>
			</a>
		</div>
	{/each}
</div>

<h2>Cast</h2>
<div class="overflow-x-auto">
	<table class="table">
		<!-- head -->
		<thead>
			<tr>
				<th>Name</th>
				<th>Character</th>
			</tr>
		</thead>
		<tbody>
			{#each data.movie.castorcrew
				.filter((mcoc) => mcoc.is_cast)
				.sort((a, b) => order_cast_crew(a.credit_order, b.credit_order)) as mcoc}
				{@const character = mcoc.character_name || 'N/A'}
				<tr class="hover:bg-base-300">
					<td>
						<a href="/p/{mcoc.person.id}">
							{mcoc.person.name}
						</a>
					</td>
					<td>{character}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
