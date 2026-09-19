<script lang="ts">
	import type { TableType } from './table_type'

	let {
		data,
		show_yesterday = true,
		show_last_week = true,
		show_theater_change = true,
		show_days_in_release = true
	}: {
		data: TableType[]
		show_yesterday?: boolean
		show_last_week?: boolean
		show_theater_change?: boolean
		show_days_in_release?: boolean
	} = $props()

	let array_data = $state(data)

	$effect(() => {
		array_data = data
	})

	const default_sort = {
		column: 'revenue',
		direction: 'desc'
	}

	let sort = $state({
		column: default_sort.column,
		direction: default_sort.direction
	})

	$effect(() => {
		$inspect(sort, 'sort')
		array_data.sort((a, b) => {
			if (sort.direction === 'asc') {
				return a[sort.column] > b[sort.column] ? 1 : -1
			} else {
				return a[sort.column] < b[sort.column] ? 1 : -1
			}
		})
	})

	const change_sort = (column: string, direction: 'asc' | 'desc', turn_off: boolean = true) => {
		if (sort.column === column) {
			if (turn_off) {
				if (sort.direction === direction) {
					sort.column = default_sort.column
					sort.direction = default_sort.direction
				} else {
					sort.direction = direction
				}
			} else {
				sort.direction = sort.direction === 'asc' ? 'desc' : 'asc'
			}
		} else {
			sort.column = column
			sort.direction = direction
		}
	}

	const tableClasses = (boxofficeday: TableType) => {
		return `hover:bg-base-200 ${boxofficeday.is_new_release ? 'bg-base-200 hover:bg-base-300' : ''} ${boxofficeday.is_estimate ? 'italic' : ''} ${boxofficeday.is_prediction ? 'border-x-6 border-error border-t-0 border-b-0' : ''}`
	}
</script>

{#snippet sortableHeader(column: string, column_name: string)}
	<div class="flex gap-2">
		<button onclick={() => change_sort(column, 'asc', false)}>
			{column_name}
		</button>
		<span class="grid grid-rows-2">
			<button
				onclick={() => {
					change_sort(column, 'asc')
				}}
				aria-label="Sort ascending"
			>
				<svg
					viewBox="0 0 24 24"
					class="h-4 {sort.direction === 'asc' && sort.column === column
						? 'fill-primary'
						: 'fill-black'}"
				>
					<path
						d="M3 19h18a1.002 1.002 0 0 0 .823-1.569l-9-13c-.373-.539-1.271-.539-1.645 0l-9 13A.999.999 0 0 0 3 19z"
					/>
				</svg>
			</button>
			<button
				onclick={() => {
					change_sort(column, 'desc')
				}}
				aria-label="Sort descending"
			>
				<svg
					viewBox="0 0 24 24"
					class="h-4 {sort.direction === 'desc' && sort.column === column
						? 'fill-primary'
						: 'fill-black'}"
				>
					<path
						d="M11.178 19.569a.998.998 0 0 0 1.644 0l9-13A.999.999 0 0 0 21 5H3a1.002 1.002 0 0 0-.822 1.569l9 13z"
					/>
				</svg>
			</button>
		</span>
	</div>
{/snippet}

{#snippet isEstimate()}
	<div
		class="tooltip tooltip-left cursor-help"
		data-tip="Revenue is an estimate. Actual revenue should be posted within 24 hours."
	>
		E
	</div>
{/snippet}
{#snippet isPreview()}
	<div
		class="tooltip tooltip-left cursor-help"
		data-tip="Revenue is a preview. Previews are also included in first day gross."
	>
		P
	</div>
{/snippet}
{#snippet isNew()}
	<div class="tooltip tooltip-left cursor-help" data-tip="Movie is new to the box office.">N</div>
{/snippet}
{#snippet isPredicted()}
	<div
		class="tooltip tooltip-left cursor-help"
		data-tip="Revenue is a prediction. Prediction methodology is published in the Rice journal."
	>
		✨
	</div>
{/snippet}

<div class="overflow-x-auto">
	<table class="table">
		<!-- head -->
		<thead>
			<tr>
				<th>
					<div class="tooltip tooltip-right cursor-help" data-tip="Box office rank for the day">
						Rank
					</div>
				</th>
				<th>
					{@render sortableHeader('title', 'Title')}
				</th>
				<th>
					{@render sortableHeader('revenue', 'Revenue')}
				</th>
				{#if show_yesterday}
					<th>
						<div
							class="tooltip tooltip-bottom cursor-help"
							data-tip="Percent change from yesterday's revenue"
						>
							% YD
						</div>
					</th>
				{/if}
				{#if show_last_week}
					<th>
						<div
							class="tooltip tooltip-bottom cursor-help"
							data-tip="Percent change from last week's revenue"
						>
							% LW
						</div>
					</th>
				{/if}
				{#if show_days_in_release}
					<th>
						{@render sortableHeader('days_in_release', 'Days in Release')}
					</th>
				{/if}
				<th>
					{@render sortableHeader('theaters', 'Theaters')}
				</th>
				{#if show_theater_change}
					<th>
						<div
							class="tooltip tooltip-bottom cursor-help"
							data-tip="Change from last week's theater count"
						>
							{@render sortableHeader('theater_change', 'Theater Change')}
						</div>
					</th>
				{/if}
				<th>
					{@render sortableHeader('per_theater_revenue', 'Per Theater')}
				</th>
				<th>Note</th>
			</tr>
		</thead>
		<tbody>
			{#each array_data as boxofficeday}
				<tr class={tableClasses(boxofficeday)}>
					<td class="not-italic">{boxofficeday.rank}</td>
					<td>
						<a href="/m/{boxofficeday.movie_id}" class="text-primary">
							{boxofficeday.title}
						</a></td
					>
					<td>${boxofficeday.revenue.toLocaleString()}</td>
					<!-- red or green depending on value -->
					{#if show_yesterday}
						<td
							class={boxofficeday.yesterday_revenue &&
							boxofficeday.revenue < boxofficeday.yesterday_revenue
								? 'text-error'
								: 'text-success'}
						>
							{boxofficeday.yesterday_revenue
								? `${Math.round((100 * boxofficeday.revenue) / boxofficeday.yesterday_revenue) - 100}%`
								: '-'}
						</td>
					{/if}
					{#if show_last_week}
						<td
							class={boxofficeday.last_week_revenue &&
							boxofficeday.revenue < boxofficeday.last_week_revenue
								? 'text-error'
								: 'text-success'}
						>
							{boxofficeday.last_week_revenue
								? `${Math.round((100 * boxofficeday.revenue) / boxofficeday.last_week_revenue) - 100}%`
								: '-'}
						</td>
					{/if}
					{#if show_days_in_release}
						<td>{boxofficeday.days_in_release}</td>
					{/if}
					<td>{boxofficeday.theaters}</td>
					{#if show_theater_change}
						<td
							class={boxofficeday.theater_change !== null && boxofficeday.theater_change < 0
								? 'text-error'
								: 'text-success'}
						>
							{boxofficeday.theater_change !== null && boxofficeday.theater_change > 0
								? '+'
								: ''}{boxofficeday.theater_change || '-'}
						</td>
					{/if}
					<td>${boxofficeday.per_theater_revenue}</td>
					<td class="mr-4 flex justify-center">
						{#if boxofficeday.is_preview}
							{@render isPreview()}
						{:else if boxofficeday.is_estimate}
							<!-- only render estimates if not preview -->
							{@render isEstimate()}
						{/if}
						{#if boxofficeday.is_new_release}
							{@render isNew()}
						{/if}
						{#if boxofficeday.is_prediction}
							{@render isPredicted()}
						{/if}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
