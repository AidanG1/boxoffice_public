<!-- daily grosses -->
<script lang="ts">
	import BoxOfficeTable from '$lib/components/BoxOfficeTable.svelte'
	import { addDays, dateToYmd, isWithinBoxOfficeNavigationRange, parseDateString } from '$lib/utils'
	import RecapImage from './RecapImage.svelte'

	let { data } = $props()

	let date = $state(parseDateString(data.date || ''))

	$effect(() => {
		if (data.date) {
			date = parseDateString(data.date)
		}
	})

	let in_future = $state(false)
	$effect(() => {
		// if any of the box office data are predictions
		in_future = data.boxoffice.some((item) => item.is_prediction)
	})

	const moveButtonHref = (day_change: number) => `/day/${dateToYmd(addDays(date, day_change))}`
	const canMoveTo = (day_change: number) => isWithinBoxOfficeNavigationRange(addDays(date, day_change))
</script>

<svelte:head>
	<title>
		Box Office Data for {date.toLocaleDateString('en-US', {
			weekday: 'long',
			month: 'long',
			day: 'numeric',
			year: 'numeric'
		})}
	</title>
</svelte:head>

{#snippet header()}
	<h1 class="px-2 text-2xl font-bold text-center">
		{#if in_future}
			<span class="text-error">Predicted</span>
		{/if}
		Box Office for {date.toLocaleDateString('en-US', {
			weekday: 'short',
			month: 'long',
			day: 'numeric',
			year: 'numeric'
		})}
	</h1>
{/snippet}

{#snippet move_button(day_change: number, label: string)}
	{#if canMoveTo(day_change)}
		<a href={moveButtonHref(day_change)} class="btn btn-primary">
			{label}
		</a>
	{:else}
		<span class="btn btn-primary invisible" aria-hidden="true">{label}</span>
	{/if}
{/snippet}

<div class="p-2">
	<div class="mb-4 hidden items-center justify-between md:flex">
		<!-- link to previous day -->
		{@render move_button(-1, 'Previous')}
		{@render header()}
		<!-- link to next day -->
		{@render move_button(1, 'Next')}
	</div>
	<div class="flex flex-col items-center justify-between md:hidden">
		{@render header()}
		<div class="flex w-full justify-between mt-2">
			{@render move_button(-1, 'Previous')}
			{@render move_button(1, 'Next')}
		</div>
	</div>

	<BoxOfficeTable
		data={data.boxoffice}
		show_days_in_release={!in_future}
		show_theater_change={!in_future}
	/>
</div>

<!-- <RecapImage data={data.boxoffice} date={date} type="Day" /> -->
