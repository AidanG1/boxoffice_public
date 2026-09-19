<script lang="ts">
	import { parseDateString, type MovieData } from '$lib/utils'
	import { getMovieWeekends, formatKMB } from '$lib/utils'

	let { movie_id }: { movie_id: string } = $props()
</script>

{#await getMovieWeekends(movie_id)}
	<div class="p-2">Loading weekend data...</div>
{:then weekends}
	<h2>Weekend Table</h2>
	<div class="overflow-x-auto">
		<table class="table">
			<!-- head -->
			<thead>
				<tr>
					<th>Date</th>
					<th>Weekend Revenue</th>
					<th>% LW</th>
					<th>Weekend Theaters</th>
				</tr>
			</thead>
			<tbody>
				{#each weekends as weekend, i}
					{@const revenue_change =
						i > 0
							? ((weekend.weekend_revenue - weekends[i - 1].weekend_revenue) /
									weekends[i - 1].weekend_revenue) *
								100
							: 0}
					<tr class="hover:bg-base-300">
						<td>
							<a href="/weekend/{weekend.weekend_start_date}">
								{new Date(parseDateString(weekend.weekend_start_date)).toLocaleDateString('en-US', {
									weekday: 'short',
									month: 'short',
									day: 'numeric',
									year: 'numeric'
								})}
							</a>
						</td>
						<td>${formatKMB(weekend.weekend_revenue, 2)}</td>
						<td class={revenue_change < 0 ? 'text-error' : 'text-success'}>
							{revenue_change < 0 ? '' : '+'}
							{revenue_change.toFixed(2)}%
						</td>
						<td>{weekend.weekend_theaters}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{:catch error}
	<div class="text-error p-2">
		Error loading weekend data: {error.message}
	</div>
{/await}
