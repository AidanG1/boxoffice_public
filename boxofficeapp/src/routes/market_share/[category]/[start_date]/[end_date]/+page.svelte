<script lang="ts">
	import { goto } from '$app/navigation'
	import { formatKMB } from '$lib/utils'
	import { scaleBand } from 'd3-scale'
	import { Bars, Chart, PieChart, Svg, Tooltip, Axis, Highlight, RectClipPath } from 'layerchart'

	let { data } = $props()

	$inspect(data, 'market share data')

	const add_colors_to_data = (data: any[]) => {
		return data
			.filter((item) => item.total_revenue > 0)
			.map((item, index) => ({
				...item,
				color:
					item.category_item === 'Others'
						? 'var(--color-neutral)'
						: `var(--color-${['accent', 'success', 'warning', 'error', 'info'][index % 5]})`
			}))
	}

	let loading = $state(false)
</script>

<div class="p-2">
	<h1>
		Market Share for <span class="text-primary">
			<select
				onchange={(event) => {
					const selectedCategory = event.target.value
					loading = true
					goto(`/market_share/${selectedCategory}/${data.start_date}/${data.end_date}`)
				}}
			>
				{#each Object.keys(data.category_to_display_map) as c}
					<option value={c} selected={c === data.category} class="text-base">
						{data.category_to_display_map[c]}
					</option>
				{/each}
			</select>
		</span>
		from
		<input
			class="text-primary"
			type="date"
			value={data.start_date}
			onchange={(event) => {
				const newStartDate = event.target.value
				loading = true
				goto(`/market_share/${data.category}/${newStartDate}/${data.end_date}`)
			}}
		/>
		to
		<input
			class="text-primary"
			type="date"
			value={data.end_date}
			onchange={(event) => {
				const newEndDate = event.target.value
				loading = true
				goto(`/market_share/${data.category}/${data.start_date}/${newEndDate}`)
			}}
		/>
	</h1>
	{#if loading}
		<div class="flex h-[200px] items-center justify-center">
			<div class="loading loading-spinner loading-lg"></div>
		</div>
	{/if}
	<div class="group h-[300px] resize rounded border p-4">
		<Chart
			data={add_colors_to_data(data.market_share)}
			x="category_item"
			xScale={scaleBand().padding(0.4)}
			yDomain={[0, null]}
			yNice={4}
			y="market_share"
			padding={{ left: 16, bottom: 24 }}
			tooltip={{ mode: 'band' }}
		>
			<Svg>
				<Axis
					placement="bottom"
					grid
					rule
					tickLabelProps={{
						rotate: -5,
						class: 'font-semibold'
					}}
				/>
				<Axis placement="left" rule format={(v) => `${(v * 100).toFixed(0)}%`} />
				<Bars strokeWidth={1} class="fill-primary group-hover:fill-neutral transition-colors" />
				<Highlight
					area
					bar={{ class: 'fill-primary bg-red-100 hover:fill-transparent', strokeWidth: 1 }}
				/>
			</Svg>
			<Tooltip.Root
				let:data
				class="border-1 bg-base-200/70 mt-1 whitespace-nowrap bg-opacity-50 p-1"
			>
				<Tooltip.Header>
					{data.category_item}
				</Tooltip.Header>
				<Tooltip.List>
					<Tooltip.Item label="Market Share" value={`${(data.market_share * 100).toFixed(2)}%`} />
				</Tooltip.List>
			</Tooltip.Root>
		</Chart>
	</div>
	{#if data.sum_more_than_one}
		<div role="alert" class="alert alert-warning">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				fill="none"
				viewBox="0 0 24 24"
				class="stroke-warning-content h-6 w-6 shrink-0"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				></path>
			</svg>
			<span>
				The sum of market shares is greater than 100%. This is expected for categories like "TMDB
				Genre" or "Production Company" where movies can belong to multiple categories.</span
			>
		</div>
	{:else}
		<div role="alert" class="alert alert-info">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				fill="none"
				viewBox="0 0 24 24"
				class="stroke-info-content h-6 w-6 shrink-0"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				></path>
			</svg>
			<span>
				The sum of market shares is less than or equal to 100%. This is expected for categories like
				"MPAA Rating" or "Numbers Genre" where movies belong to a single category.</span
			>
		</div>
	{/if}
	<!-- 
	<div class="h-[300px] resize overflow-auto rounded border p-4">
		<PieChart
			data={add_colors_to_data(data.market_share)}
			key="category_item"
			value="total_revenue"
			legend={{ placement: 'top-left', orientation: 'vertical' }}
			c="color"
		/>
	</div> -->

	<table class="mt-4 table w-full">
		<thead>
			<tr>
				<th>Category Item</th>
				<th>Market Share</th>
				<th>Total Revenue</th>
			</tr>
		</thead>
		<tbody>
			{#each add_colors_to_data(data.market_share) as item}
				<tr>
					<td class="text-primary"><a href={`/${data.category}/${item.category_item.replace('/', '-')}`}>{item.category_item}</a></td>
					<td>
						{(item.market_share * 100).toFixed(2)}%
					</td>
					<td>
						${item.total_revenue ? formatKMB(item.total_revenue, 2) : 'N/A'}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
