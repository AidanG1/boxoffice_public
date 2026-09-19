<script lang="ts">
	import { formatKMB, parseDateString, type MovieData } from '$lib/utils'

	let {
		data,
	}: {
		data: MovieData
	} = $props()
</script>

<h2>Comps</h2>
<p>
	Comps are similar or <em>comparison</em> movies that are used for analysis and marketing purposes.
	The way they are found is described in more detail in the
	<a href="https://repository.rice.edu/items/0705cb7e-f675-4b07-a557-dacba382b691" target="_blank"
		>paper
	</a>. Comps always have release dates before the movie they are compared to.
</p>

<div class="overflow-x-auto">
	<table class="table">
		<!-- head -->
		<thead>
			<tr>
				<th>Title</th>
				<th>Release Date</th>
				<th>Budget</th>
			</tr>
		</thead>
		<tbody>
			{#each data.movie.movie_comps as comp}
				<tr class="hover:bg-base-300">
					<td>
						<a href={`/m/${comp.comp_id.id}`}>
							{comp.comp_id.title}
						</a>
					</td>
					<td
						>{new Date(parseDateString(comp.comp_id.release_date)).toLocaleDateString('en-US', {
							year: 'numeric',
							month: 'short',
							day: 'numeric'
						})}</td
					>
					<td>${formatKMB(comp.comp_id.budget)}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
