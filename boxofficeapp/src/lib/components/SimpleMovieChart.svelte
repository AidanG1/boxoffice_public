<script lang="ts">
	// take in movie info days and return a chart of the wikipedia page views
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
		LineChart,
		Line,
		Text,
		Grid
	} from 'layerchart'
	import { type MovieData, format, formatKMB, parseDateString } from '$lib/utils'
	import { scaleBand } from 'd3-scale'

	let {
		movie_data,
		text_color = 'white',
		line_color = '#d4aaff',
		movie_title_in_title = false
	}: {
		movie_data: MovieData
		text_color: string
		line_color: string
		movie_title_in_title?: boolean
	} = $props()

	const addDaysToMovieData = (movie_data: MovieData) => {
		return movie_data.boxofficedays.map((day) => {
			return {
				...day,
				date: parseDateString(day.date)
			}
		}).filter((day) => day.is_preview === false)
	}
</script>

<div class="mb-2 text-center text-lg font-semibold" style="color: {text_color}">
	<a href="/m/{movie_data.movie.id}" class="flex items-center justify-center">
		Daily Grosses {#if movie_title_in_title}for&nbsp;<em>{movie_data.movie.title}</em>{/if}
		<svg
			viewBox="8 0 24 24"
			fill="none"
			xmlns="http://www.w3.org/2000/svg"
			class="inline h-6 w-6"
			style="fill: {text_color};"
		>
			<path
				d="M14 2C14 1.44772 14.4477 1 15 1H21C22.1046 1 23 1.89543 23 3V9C23 9.55229 22.5523 10 22 10C21.4477 10 21 9.55228 21 9V4.41421L13.4406 11.9736C13.0501 12.3641 12.4169 12.3641 12.0264 11.9736C11.6359 11.5831 11.6359 10.9499 12.0264 10.5594L19.5858 3H15C14.4477 3 14 2.55228 14 2Z"
			/>
		</svg>
	</a>
</div>
<div class="my-2 h-[200px]">
	<LineChart
		data={addDaysToMovieData(movie_data)}
		x="date"
		y="revenue"
		xScale={scaleBand().padding(0.2)}
		series={[{ key: 'wikipedia_views', color: line_color }]}
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
					rule: `stroke-${text_color}`,
					tick: `stroke-${text_color}`,
					tickLabel: `fill-${text_color} font-semibold`
				}}
				tickLabelProps={{
					style: `fill: ${text_color}`
				}}
				ticks={Math.floor(movie_data.movie_info_days.length / 10)}
			/>
			<Axis
				placement="left"
				rule
				format={(v) => formatKMB(v)}
				classes={{
					rule: `stroke-${text_color}`,
					tick: `stroke-${text_color}`,
					tickLabel: `fill-${text_color} font-semibold`
				}}
				tickLabelProps={{
					style: `fill: ${text_color}`
				}}
			/>
			<Grid
				y={{
					style: `stroke-dasharray: 2, 2; stroke: ${text_color === 'white' ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)'};`
				}}
			/>
			<Spline class="stroke-2" style={`stroke: ${line_color};`} y="revenue" />
			<Highlight points={{ style: `fill: ${line_color}` }} />
		</Svg>
		<Tooltip.Root
			let:data
			class="mt-1 border-1 p-1 whitespace-nowrap {text_color === 'white'
				? 'bg-black/50'
				: 'bg-white/50'} bg-opacity-50"
		>
			<Tooltip.Header>
				{format(data.date, 'eee, MMMM do')}
			</Tooltip.Header>
			<Tooltip.Item label="Revenue" value={formatKMB(data.revenue, 2)} />
		</Tooltip.Root>
	</LineChart>
</div>

<ul class="w-full space-y-1 text-left text-base text-gray-300">
	<li>
		<span class="font-semibold text-white">Total Gross:</span>
		<span class="font-bold text-green-400">
			${formatKMB(movie_data.boxofficedays.reduce((acc, day) => acc + day.revenue, 0), 2)}
		</span>
	</li>
	<li>
		<span class="font-semibold text-white">Max Theater Count:</span>
		<span class="font-bold text-green-500">▲ {Math.max(...movie_data.boxofficedays.map(day => day.theaters))}</span>
	</li>
</ul>
