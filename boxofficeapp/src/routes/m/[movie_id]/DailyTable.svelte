<script lang="ts">
	import { parseDateString, type MovieData } from '$lib/utils'

	let {
		data,
	}: {
		data: MovieData
	} = $props()
</script>

<h2>Daily Table</h2>
<div class="overflow-x-auto">
	<table class="table">
		<!-- head -->
		<thead>
			<tr>
				<th>Date</th>
				<th>Revenue</th>
				<th>% YD</th>
				<th>Theaters</th>
			</tr>
		</thead>
		<tbody>
			{#each data.boxofficedays as bod, index}
				{@const yesterday_revenue = data.boxofficedays[index - 1]?.revenue || 0}
				{@const yesterday_change = yesterday_revenue
					? ((bod.revenue - yesterday_revenue) / yesterday_revenue) * 100
					: 0}
				<tr class="hover:bg-base-300">
					<td>
						<a href="/day/{bod.date}">
							{new Date(parseDateString(bod.date)).toLocaleDateString('en-US', {
								weekday: 'short',
								month: 'short',
								day: 'numeric',
								year: 'numeric'
							})}
						</a>
					</td>
					<td>${bod.revenue.toLocaleString()}</td>
					<td class={yesterday_change < 0 ? 'text-error' : 'text-success'}>
						{yesterday_change < 0 ? '' : '+'}
						{yesterday_change.toFixed(2)}%
					</td>
					<td>{bod.theaters}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
