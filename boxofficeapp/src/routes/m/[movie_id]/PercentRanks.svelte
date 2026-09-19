<script lang="ts">
	import { filter_name_to_title } from '$lib/screener'
	import { formatKMB, getPercentRanks } from '$lib/utils'

	let { movie_id }: { movie_id: string } = $props()

	// value format types
	let value_format = (category: string, value: number) => {
		const kmb_categories = [
			'youtube_sum_all_views',
			'budget',
			'max_daily_revenue',
			'opening_weekend_revenue',
            'domestic_revenue',
            'opening_day_revenue',
			'worldwide_box_office',
			'international_box_office',
			'preview_revenue',
		]
		const locale_categories = [
			'imdb_rating',
			'metacritic_rating',
			'rotten_tomatoes_rating',
			'letterboxd_rating',
			'legs',
			'gross_to_budget_ratio'
		]

        if (kmb_categories.includes(category)) {
            return formatKMB(value, 2)
        } else if (locale_categories.includes(category) && value !== null) {
            return value.toLocaleString('en-US', { maximumFractionDigits: 2 })
        } else if (value === null) {
			return 'N/A'
		} else {
			return value.toLocaleString('en-US')
		}
	}
</script>

{#await getPercentRanks(movie_id)}
	<div class="p-2">Loading percent ranks...</div>
{:then percentRanks}
	{@const sorted_ranks = percentRanks.sort((a, b) => b['percent_rank'] - a['percent_rank'])}
	<div class="p-2">
		<h2>Percent Ranks</h2>
		<table class="table">
			<thead>
				<tr>
					<th>Category</th>
					<th>Value</th>
					<th>Percent Rank</th>
				</tr>
			</thead>
			<tbody>
				{#each sorted_ranks as val}
					<tr class="hover:bg-base-300">
						<td>{filter_name_to_title(val['category'])}</td>
						<td>{value_format(val['category'], val['value'])}</td>
						<td>{(val['percent_rank'] * 100).toFixed(2)}%</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{:catch error}
	<div class="text-error p-2">
		Error loading percent ranks: {error.message}
	</div>
{/await}
