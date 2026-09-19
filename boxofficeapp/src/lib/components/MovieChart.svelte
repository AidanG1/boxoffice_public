<script lang="ts">
	import type { Tables } from '$lib/supabase.types'
	import {
		Tooltip,
		Svg,
		Axis,
		Chart,
		Spline,
		Highlight,
		MotionPath,
		Bars,
		LineChart
	} from 'layerchart'
	import { linear } from 'svelte/easing'
	import {
		getMovieData,
		type MovieData,
		format,
		formatKMB,
		parseDateString,
		type PredictionData
	} from '$lib/utils'
	import SearchMovie from './SearchMovie.svelte'
	import { scaleBand, scaleLog, scaleLinear } from 'd3-scale'

	let {
		movie_data,
		prediction_data
	}: {
		movie_data: MovieData
		prediction_data: PredictionData
	} = $props()

	let cumulative = $state(false)
	let log_scale = $state(false)
	let show_theater_counts = $state(true)
	let show_per_theater = $state(false)
	let chartData: {
		date: Date
		index: number
		revenue: number
		base_revenue: number
		theaters: number
		theaters_scaled: number
		per_theater?: number
		compare_1?: number
		compare_2?: number
		compare_3?: number
		compare_4?: number
		compare_5?: number
		prediction?: number
	}[] = $state([])

	let compare_movies: MovieData[] = $state([])
	let chart_max_revenue: number = $state(0)
	let chart_min_revenue: number = $state(0)

	const compare_colors: string[] = ['info', 'success', 'warning', 'error', 'accent']

	const makeCumulative = (data: (number | null)[], base_value: number = 0) => {
		// start with a base value if provided
		if (data.length === 0) return []

		let accumulated_values = []
		let accumulated_sum = base_value

		for (let i = 0; i < data.length; i++) {
			const value = data[i]
			if (value === null) {
				accumulated_values.push(null)
			} else {
				accumulated_sum += value
				accumulated_values.push(accumulated_sum)
			}
		}
		return accumulated_values
	}

	const createData = (cumulative: boolean, compare_movies: MovieData[]) => {
		let data = removePreviews(movie_data.boxofficedays)
		let predictions: (number | null)[] = []
		let net_prediction_length = 0

		if (prediction_data) {
			const prediction_start_date = parseDateString(prediction_data.start_date)

			const start_date_index = data.findIndex(
				(d) => parseDateString(d.date).getTime() >= prediction_start_date?.getTime()
			)

			const prediction_length = prediction_data.predictions.length || 0
			net_prediction_length = prediction_length - (data.length - start_date_index)

			const null_values: (number | null)[] = Array.from({ length: start_date_index }, () => null)
			predictions = null_values.concat(prediction_data.predictions)
		}

		let base_revenues: (number | null)[] = data.map((d) => d.revenue)
		let revenues: (number | null)[] = data.map((d) => d.revenue)

		// add null revenue days for prediction length
		let last_date = parseDateString(data[data.length - 1].date).getTime()
		for (let i = 0; i < net_prediction_length; i++) {
			let next_date = new Date(last_date + (i + 1) * 24 * 60 * 60 * 1000)
			data.push({
				date: next_date.toISOString().split('T')[0],
				revenue: null,
				theaters: null
			})
			base_revenues.push(null)
			revenues.push(null)
		}

		let compare_1: (number | null)[] = []
		let compare_2: (number | null)[] = []
		let compare_3: (number | null)[] = []
		let compare_4: (number | null)[] = []
		let compare_5: (number | null)[] = []

		for (let i = 0; i < compare_movies.length; i++) {
			const movieData = compare_movies[i]

			// remove previews from comparison data
			const movieDataDays = removePreviews(movieData.boxofficedays)

			const movieRevenues = movieDataDays.map((d) => d.revenue)
			if (i === 0) {
				compare_1 = movieRevenues
			} else if (i === 1) {
				compare_2 = movieRevenues
			} else if (i === 2) {
				compare_3 = movieRevenues
			} else if (i === 3) {
				compare_4 = movieRevenues
			} else if (i === 4) {
				compare_5 = movieRevenues
			}
		}

		if (cumulative) {
			revenues = makeCumulative(revenues)
			compare_1 = makeCumulative(compare_1)
			compare_2 = makeCumulative(compare_2)
			compare_3 = makeCumulative(compare_3)
			compare_4 = makeCumulative(compare_4)
			compare_5 = makeCumulative(compare_5)

			const last_revenue_not_null = revenues.findLast((r) => r !== null)
			const first_prediction_value = predictions.find((p) => p !== null) ?? 0

			// Subtract first prediction value if first prediction overlaps last revenue
			predictions = makeCumulative(predictions, last_revenue_not_null - first_prediction_value)
		}

		const chartValues = [
			...base_revenues,
			...revenues,
			...compare_1,
			...compare_2,
			...compare_3,
			...compare_4,
			...compare_5,
			...predictions
		].filter((v) => v !== null)

		chart_min_revenue = Math.min(...chartValues)
		chart_max_revenue = Math.max(...chartValues)
		const largest_theater_count = Math.max(...data.map((d) => d.theaters || 0))

		return data.map((d, index) => {
			const date = parseDateString(d.date)
			const revenue = revenues[index]
			const base_revenue = base_revenues[index]
			const theaters = d.theaters || null

			return {
				date,
				index,
				revenue,
				base_revenue,
				theaters,
				theaters_scaled: Math.round(theaters * (chart_max_revenue / largest_theater_count)),
				per_theater: theaters > 0 ? base_revenue / theaters : 0,
				compare_1: compare_1[index] || 0,
				compare_2: compare_2[index] || 0,
				compare_3: compare_3[index] || 0,
				compare_4: compare_4[index] || 0,
				compare_5: compare_5[index] || 0,
				prediction: predictions[index] || null
			}
		})
	}

	const removePreviews = (data: Tables<'boxofficeday'>[]) => {
		return data.filter((d) => d.is_preview === false)
	}

	$effect(() => {
		chartData = createData(cumulative, compare_movies)
	})

	let innerWidth = $state(0)
	let settingsModal: HTMLDialogElement | null = $state(null)
</script>

<svelte:window bind:innerWidth />

{#if movie_data.boxofficedays.length === 0}
	<div class="mt-4 text-center text-lg font-semibold">No box office data yet for this movie.</div>
{:else}
	{#snippet chart_compare()}
		<SearchMovie
			select_function={(result) => {
				getMovieData(result.id).then((movieData) => {
					if (
						compare_movies.length < 5 &&
						!compare_movies.some((m) => m.movie.id === movieData.movie.id)
					) {
						compare_movies = [...compare_movies, movieData]
						show_theater_counts = false
					}
				})
			}}
			placeholder="Compare"
		/>
	{/snippet}

	{#snippet chart_settings()}
		<label class="label">
			<input type="checkbox" bind:checked={cumulative} class="toggle" />
			Cumulative
		</label>

		<label class="label">
			<input type="checkbox" bind:checked={log_scale} class="toggle" />
			Log Scale
		</label>

		<label class="label">
			<input type="checkbox" bind:checked={show_theater_counts} class="toggle" />
			Show Theater Counts
		</label>

		<label class="label">
			<input type="checkbox" bind:checked={show_per_theater} class="toggle" />
			Show Per Theater Revenue
		</label>
	{/snippet}

	<!-- slider for cumulative vs daily -->
	<!-- the button is on the bottom when the view is small -->
	<div class="mt-4 hidden items-center justify-between md:flex">
		<div>
			{@render chart_settings()}
		</div>
		{@render chart_compare()}
	</div>

	{#if compare_movies.length > 0}
		<div class="mb-2 flex">
			{#each compare_movies as movie, index}
				<div
					class="badge badge-{compare_colors[index % compare_colors.length]} mr-2 flex items-center"
				>
					<a href={`/m/${movie.movie.id}`} class="text-white!">
						{movie.movie.title}
					</a>
					<button
						class="btn btn-sm btn-circle btn-ghost ml-2"
						onclick={() => {
							compare_movies = compare_movies.filter((m) => m.movie.id !== movie.movie.id)
						}}
					>
						✕
					</button>
				</div>
			{/each}
		</div>
	{/if}
	<div
		class="bg-base-300/70 mt-2 rounded border p-4"
		style={innerWidth < 640 ? `width: calc(${innerWidth}px - 1rem)` : ``}
	>
		<!-- chart title -->
		<div class="mb-2 text-center text-lg font-semibold">
			{movie_data.movie.title} Revenue
			{#if cumulative}
				(Cumulative)
			{:else}
				(Daily)
			{/if}
			{#if log_scale}
				(Log Scale)
			{/if}
			{#if show_theater_counts}
				(with Theater Counts)
			{/if}
		</div>
		<div class="grid-stack grid h-[300px]">
			<Chart
				data={chartData}
				x={compare_movies.length > 0 ? 'index' : 'date'}
				y={['revenue']}
				xScale={scaleBand().padding(0.2)}
				yScale={log_scale ? scaleLog().base(2) : scaleLinear()}
				yDomain={log_scale
					? [chart_min_revenue * 0.9 + 1, chart_max_revenue]
					: [1, chart_max_revenue]}
				yNice
				padding={{ left: 16, bottom: 24 }}
				tooltip={{ mode: 'bisect-x' }}
				width={50}
			>
				<Svg>
					<Axis
						placement="left"
						grid
						format={(v) => formatKMB(v, 1)}
						classes={{
							rule: `stroke-base-content/50`,
							tick: `stroke-base-content`,
							tickLabel: `fill-base-content font-semibold`
						}}
						tickLabelProps={{
							style: `fill: base-content`
						}}
						ticks={(scale) => scale.ticks?.().filter((tick) => tick !== 0)}
					/>
					<Axis
						placement="bottom"
						format={(v) => {
							if (compare_movies.length > 0) {
								return v.toString()
							} else {
								const date = new Date(v)
								return `${date.getMonth() + 1}/${date.getDate()}`
							}
						}}
						classes={{
							tick: `stroke-base-content`,
							tickLabel: `fill-base-content font-semibold`
						}}
						tickLabelProps={{
							style: `fill: base-content`
						}}
						ticks={Math.round(chartData.length / 10)}
					/>
					{#if show_theater_counts}
						<Bars
							strokeWidth={1}
							y="theaters_scaled"
							class={`fill-base-content stroke-primary opacity-30 transition-colors`}
						/>
					{/if}
					{#each compare_movies as movie, index}
						<MotionPath duration="2s">
							<Spline
								draw={{ duration: 2000, easing: linear }}
								class={`stroke-2 stroke-${compare_colors[index % compare_colors.length]}`}
								y={index === 0
									? 'compare_1'
									: index === 1
										? 'compare_2'
										: index === 2
											? 'compare_3'
											: index === 3
												? 'compare_4'
												: 'compare_5'}
							/>
						</MotionPath>
					{/each}
					{#key movie_data}
						<MotionPath duration="2s">
							<Spline
								draw={{ duration: 2000, easing: linear }}
								class={`stroke-4 stroke-primary`}
								y="revenue"
							/>
						</MotionPath>
					{/key}
					{#if prediction_data}
						<MotionPath duration="1s">
							<Spline
								class="stroke-4 stroke-secondary [stroke-dasharray:3,3]"
								y="prediction"
								draw={{ duration: 1000, easing: linear, delay: 2000 }}
							/>
						</MotionPath>
						<Highlight points={{ class: `fill-secondary` }} y={(d) => d.prediction} />
					{/if}
					<Highlight points={{ class: `fill-primary` }} y={(d) => d.revenue} />
				</Svg>
				<Tooltip.Root
					let:data
					class="border-1 bg-base-200/50 mt-1 whitespace-nowrap bg-opacity-50 p-1"
				>
					<Tooltip.Header>
						{format(data.date, 'eee, MMMM do')}
					</Tooltip.Header>
					<Tooltip.List>
						{#if data.revenue !== null}
							<Tooltip.Item
								classes={{
									label: `font-semibold`
								}}
								label={movie_data.movie.title}
								value={`\$${formatKMB(data.revenue, 2)}`}
							/>
						{/if}
						{#if prediction_data && data.prediction !== null}
							<Tooltip.Item
								classes={{
									label: `font-semibold`
								}}
								label="Predicted Revenue"
								value={`\$${formatKMB(data.prediction, 2)}`}
							/>
						{/if}
						{#if show_theater_counts && data.theaters !== null}
							<Tooltip.Item
								classes={{
									label: `font-semibold`
								}}
								label="Theaters"
								value={data.theaters.toString()}
							/>
						{/if}
						{#each compare_movies as movie, index}
							<Tooltip.Item
								classes={{
									label: `font-semibold`
								}}
								label={movie.movie.title}
								value={`\$${formatKMB(data[`compare_${index + 1}`], 2)}`}
							/>
						{/each}
					</Tooltip.List>
				</Tooltip.Root>
			</Chart>
			<!-- <LineChart
		data={dateSeriesData}
		x="date"
		{renderContext}
		{debug}
		series={[{ key: 'value', color: 'var(--color-secondary)' }]}
	>
		<Svg>
			<Axis placement="bottom" rule />
			<Axis placement="left" rule format={(v) => v || ''} />
		</Svg>
	</LineChart> -->
		</div>
		{#if show_per_theater}
			<hr />
			<div class="mb-2 text-center text-lg font-semibold">Revenue Per Theater</div>
			<div class="mt-2 h-[150px]">
				<LineChart
					data={chartData}
					x="date"
					y="per_theater"
					xScale={scaleBand().padding(0.2)}
					series={[{ key: 'per_theater' }]}
				>
					<Svg>
						<Axis
							placement="bottom"
							rule
							format={(v) => {
								const date = new Date(v)
								return `${date.getMonth() + 1}/${date.getDate()}`
							}}
							classes={{
								rule: `stroke-base-content`,
								tick: `stroke-base-content`,
								tickLabel: `fill-base-content font-semibold`
							}}
							tickLabelProps={{
								style: `fill: base-content`
							}}
							ticks={Math.round(chartData.length / 10)}
						/>
						<Axis
							placement="left"
							rule
							format={(v) => formatKMB(v, 1)}
							classes={{
								rule: `stroke-base-content`,
								tick: `stroke-base-content`,
								tickLabel: `fill-base-content font-semibold`
							}}
							tickLabelProps={{
								style: `fill: base-content`
							}}
						/>
						<Spline class="stroke-primary stroke-2" y="per_theater" />
						<Highlight points lines />
					</Svg>
					<Tooltip.Root
						let:data
						class="bg-base-200/80 mt-1 whitespace-nowrap rounded border p-1 font-semibold"
					>
						<Tooltip.Header>
							{format(data.date, 'eee, MMMM do')}
						</Tooltip.Header>
						<Tooltip.Item
							label="Per Theater Revenue"
							value={`\$${formatKMB(data.per_theater, 2)}`}
							classes={{
								label: `font-semibold`
							}}
						/>
					</Tooltip.Root>
				</LineChart>
			</div>
		{/if}
	</div>

	<button class="btn btn-sm mt-2 inline-block md:hidden" onclick={() => settingsModal?.showModal()}>
		Chart Settings
	</button>
	<!-- Open the modal using ID.showModal() method -->
	<dialog bind:this={settingsModal} class="modal">
		<div class="modal-box flex flex-col items-center justify-between">
			{@render chart_settings()}
			{@render chart_compare()}
		</div>
		<form method="dialog" class="modal-backdrop">
			<button>close</button>
		</form>
	</dialog>
{/if}
<!-- 
stroke-info 
stroke-success
stroke-warning
stroke-error
stroke-accent
badge-info
badge-success
badge-warning
badge-error
badge-accent
-->
