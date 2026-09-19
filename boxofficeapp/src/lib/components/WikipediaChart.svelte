<script lang="ts">
	// take in movie info days and return a chart of the wikipedia page views
	import {
		Tooltip,
		Svg,
		Axis,
		Chart,
		Spline,
		Highlight,
		MotionPath,
		Bars,
		LineChart,
		Line,
		Text,
		Grid
	} from 'layerchart'
	import { type MovieData, format, formatKMB, parseDateString } from '$lib/utils'
	import { scaleBand, scaleLinear, type ScaleBand, type ScaleLinear } from 'd3-scale'
	import { onMount } from 'svelte'

	let {
		movie_data,
		movie_title_in_title = false
	}: {
		movie_data: MovieData
		movie_title_in_title?: boolean
	} = $props()

	const addDaysToMovieData = (movie_data: MovieData) => {
		return movie_data.movie_info_days.map((day) => {
			return {
				...day,
				date: parseDateString(day.date)
			}
		})
	}

	let xScale: ScaleBand<string> | null = $state(null)
	let yScale: ScaleLinear<number, number> | null = $state(null)

	const get_opening_day_index = (movie_data: MovieData) => {
		const openingDay = movie_data.boxofficedays.find((day) => day.is_new_release)

		if (!openingDay) {
			// return the first date if no opening day is found
			return null
		}

		const openingDayIndex = movie_data.movie_info_days.findIndex(
			(day) => day.date === openingDay.date
		)

		return openingDayIndex
	}

	let openingDayIndex: number | null = $state(null)

	onMount(() => {
		// Initialize scales after component mounts
		const filteredMovieInfoDays = movie_data.movie_info_days.filter(
			(d) => d.wikipedia_views !== null
		)
		xScale = scaleBand()
			.domain(filteredMovieInfoDays.map((day) => day.date))
			.padding(0.2)
		yScale = scaleLinear()
			.domain([0, Math.max(...filteredMovieInfoDays.map((d) => d.wikipedia_views || 0))])
			.range([200, 0])

		openingDayIndex = get_opening_day_index(movie_data)
	})

	let clientWidth: number = $state(0)
</script>

<div class="bg-base-300/30 rounded p-4">
	<div class="mb-2 text-center text-lg font-semibold">
		<a href="https://en.wikipedia.org/wiki/{movie_data.movie.wikipedia_key}" target="_blank">
			Wikipedia Page Views {#if movie_title_in_title}for <em>{movie_data.movie.title}</em>{/if}
			<svg
				viewBox="8 0 24 24"
				fill="currentColor"
				xmlns="http://www.w3.org/2000/svg"
				class="inline h-6 w-6"
			>
				<path
					d="M14 2C14 1.44772 14.4477 1 15 1H21C22.1046 1 23 1.89543 23 3V9C23 9.55229 22.5523 10 22 10C21.4477 10 21 9.55228 21 9V4.41421L13.4406 11.9736C13.0501 12.3641 12.4169 12.3641 12.0264 11.9736C11.6359 11.5831 11.6359 10.9499 12.0264 10.5594L19.5858 3H15C14.4477 3 14 2.55228 14 2Z"
				/>
			</svg>
		</a>
	</div>
	<div class="mt-2 h-[200px]" bind:clientWidth>
		<LineChart
			data={addDaysToMovieData(movie_data)}
			x="date"
			y="wikipedia_views"
			xScale={xScale || undefined}
			yScale={yScale || undefined}
			series={[{ key: 'wikipedia_views' }]}
			yNice
			tooltip={{ mode: 'bisect-x' }}
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
					ticks={Math.floor(movie_data.movie_info_days.length / 5)}
				/>
				<Axis
					placement="left"
					rule
					format={(v) => formatKMB(v)}
					classes={{
						rule: `stroke-base-content`,
						tick: `stroke-base-content`,
						tickLabel: `fill-base-content font-semibold`
					}}
					tickLabelProps={{
						style: `fill: base-content`
					}}
				/>
				<Grid
					y={{
						style: `stroke-dasharray: 2, 2; stroke: var(--base-content); opacity: 0.5;`
					}}
				/>

				{#if openingDayIndex !== null}
					<!-- line for opening day, x1 x2 y1 y2 need to all be numbers -->
					<Line
						x1={clientWidth * (openingDayIndex / movie_data.movie_info_days.length)}
						x2={clientWidth * (openingDayIndex / movie_data.movie_info_days.length)}
						y1={0}
						y2={yScale ? 175 : 0}
						class="stroke-accent stroke-2"
					/>
					<Text
						x={clientWidth * (openingDayIndex / movie_data.movie_info_days.length) + 2}
						y={172}
						class="fill-base-content"
						value="Opening Day"
					/>
				{/if}

				<Spline class="stroke-primary stroke-2" y="wikipedia_views" />
				<Highlight points={{ style: `fill: text-primary` }} />
			</Svg>
			<Tooltip.Root
				let:data
				class="border-1 bg-base-200/50 mt-1 whitespace-nowrap bg-opacity-50 p-1"
			>
				<Tooltip.Header>
					{format(data.date, 'eee, MMMM do')}
				</Tooltip.Header>
				<Tooltip.Item label="Wikipedia Views" value={formatKMB(data.wikipedia_views, 2)} />
			</Tooltip.Root>
		</LineChart>
	</div>
</div>
