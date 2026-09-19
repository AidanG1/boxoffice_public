<!-- weekend grosses -->
<script lang="ts">
	import BoxOfficeTable from '$lib/components/BoxOfficeTable.svelte'
	import { addDays, dateToYmd, isWithinBoxOfficeNavigationRange, parseDateString } from '$lib/utils'

	let { data } = $props()

	let date = $state(parseDateString(data.date || ''))

	$effect(() => {
		if (data.date) {
			date = parseDateString(data.date)
		}
	})

	const moveButtonHref = (day_change: number) => `/weekend/${dateToYmd(addDays(date, day_change))}`
	const canMoveTo = (day_change: number) => isWithinBoxOfficeNavigationRange(addDays(date, day_change))
</script>

<svelte:head>
	<title
		>Weekend Box Office for {date.toLocaleDateString('en-US', {
			weekday: 'long',
			month: 'long',
			day: 'numeric',
			year: 'numeric'
		})}</title
	>
	<meta
		name="description"
		content="Box office data for the weekend starting {date.toLocaleDateString('en-US', {
			weekday: 'long',
			month: 'long',
			day: 'numeric',
			year: 'numeric'
		})}."
	/>
	<meta
		property="og:title"
		content={`Weekend Box Office for ${date.toLocaleDateString('en-US', {
			weekday: 'long',
			month: 'long',
			day: 'numeric',
			year: 'numeric'
		})}`}
	/>
	<meta property="og:description" content="Box office data for the weekend." />
	<meta property="og:type" content="website" />
</svelte:head>

{#snippet header()}
	<h1 class="px-2 text-2xl font-bold text-center">
		Box Office for Weekend of {date.toLocaleDateString('en-US', {
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
		{@render move_button(-7, 'Previous')}
		{@render header()}
		<!-- link to next day -->
		{@render move_button(7, 'Next')}
	</div>
	<div class="flex flex-col items-center justify-between md:hidden">
		{@render header()}
		<div class="flex w-full justify-between mt-2">
			{@render move_button(-7, 'Previous')}
			{@render move_button(7, 'Next')}
		</div>
	</div>

	{#if data.boxoffice?.length && data.boxoffice.length > 0}
		<BoxOfficeTable data={data.boxoffice} show_yesterday={false} />
	{:else}
		<div class="text-error p-2">No box office data available for this weekend.</div>
	{/if}
</div>
