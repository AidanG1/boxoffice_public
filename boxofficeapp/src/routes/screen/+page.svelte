<script lang="ts">
	import {
		filter_values,
		name_values,
		dollar_names,
		filter_name_to_title,
		type ScreenResult
	} from '$lib/screener'
	import { formatKMB } from '$lib/utils'
	import { page } from '$app/state'
	import { FilterSort } from './filterSort.svelte'
	import ScreenerImageWrapper from './ScreenerImageWrapper.svelte'

	// the URL is the single source of truth for filters and sort
	// so we will parse them from the URL on mount

	let submitButton: HTMLButtonElement | null = null

	let filterSort = new FilterSort(page.url.searchParams.get('b64') || '')

	let results: ScreenResult | null = $state(null)
	let imageModal: HTMLDialogElement | null = $state(null)
</script>

<svelte:head>
	<title>Screener</title>
	<meta name="description" content="Screen movies based on various filters and sorting options." />
</svelte:head>

<div class="p-2">
	<form>
		<div class="tabs tabs-border">
			<input type="radio" name="tabs_2" class="tab" aria-label="Filters" checked />
			<div class="tab-content border-base-300 p-6">
				<h2>Filters</h2>
				{#each filterSort.filters as filter, i}
					<div class="border-base-300 m-1 flex items-center gap-2 rounded-md border p-1">
						<button
							class="btn btn-circle btn-error mr-2"
							onclick={() => {
								filterSort.removeFilter(i)
							}}
							type="button"
						>
							&times;
						</button>
						{#if filterSort.editing_indices.includes(i)}
							<!-- edit form -->
							<select class="select" bind:value={filter.name}>
								{#each name_values as nv}
									<option value={nv}>{filter_name_to_title(nv)}</option>
								{/each}
							</select>
							<select class="select" bind:value={filter.type}>
								{#each filter_values as fv}
									<option value={fv}>{fv}</option>
								{/each}
							</select>
							<input type="value" class="input grow" bind:value={filter.value} />

							<!-- save button -->
							<button
								class="btn btn-circle btn-success"
								onclick={() => {
									filterSort.updateFilter(i, filter)
								}}
							>
								✔️
							</button>
						{:else}
							<span>{filter.name}</span>
							<span>{filter.type}</span>
							<span class="grow">{filter.value}</span>

							<!-- edit button -->
							<button
								class="btn btn-circle btn-info"
								onclick={() => {
									filterSort.editFilter(i)
								}}
								type="button"
							>
								✏️
							</button>
						{/if}
					</div>
				{/each}
				<!-- existing filters go in here -->
				<div>
					<div class="border-info bg-info m-1 flex items-center gap-2 rounded-md border p-1">
						<select class="select" bind:value={filterSort.newFilterName}>
							{#each name_values as nv}
								<option value={nv}>{filter_name_to_title(nv)}</option>
							{/each}
						</select>

						<select class="select" bind:value={filterSort.newFilterType}>
							{#each filter_values as fv}
								<option value={fv}>{fv}</option>
							{/each}
						</select>
						<input
							type="value"
							placeholder="Type here"
							class="input grow"
							bind:value={filterSort.newFilterValue}
						/>

						<button
							class="btn btn-circle btn-success"
							onclick={() => {
								filterSort.addFilter()
							}}
							type="button"
						>
							+
						</button>
					</div>
				</div>
			</div>
			<input type="radio" name="tabs_2" class="tab" aria-label="Sort" />
			<div class="tab-content border-base-300 p-6">
				<h2>Sort</h2>
				<fieldset class="fieldset bg-base-100 border-base-300 rounded-box w-64 border p-4">
					<legend class="fieldset-legend">Sort Column</legend>
					<select
						class="select"
						bind:value={filterSort.sort.name}
						bind:this={filterSort.sortNameInput}
					>
						{#each name_values as nv}
							<option value={nv}>{filter_name_to_title(nv)}</option>
						{/each}
					</select>
				</fieldset>

				<fieldset class="fieldset bg-base-100 border-base-300 rounded-box w-64 border p-4">
					<legend class="fieldset-legend">
						Sort Direction: {filterSort.sort.direction === 'asc'
							? 'Ascending'
							: 'Descending'}</legend
					>
					<label class="toggle text-base-content toggle-xl">
						<input
							type="checkbox"
							checked={filterSort.sort.direction === 'asc'}
							onchange={() => {
								filterSort.sortDirectionChanged()
							}}
						/>
						<svg
							viewBox="0 0 24 24"
							fill="none"
							xmlns="http://www.w3.org/2000/svg"
							stroke="currentColor"
						>
							<g id="Edit / Sort_Ascending">
								<path
									id="Vector"
									d="M4 17H10M4 12H13M18 11V19M18 19L21 16M18 19L15 16M4 7H16"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</g>
						</svg><svg
							viewBox="0 0 24 24"
							fill="none"
							xmlns="http://www.w3.org/2000/svg"
							stroke="currentColor"
						>
							<g id="Edit / Sort_Descending">
								<path
									id="Vector"
									d="M4 17H16M4 12H13M4 7H10M18 13V5M18 5L21 8M18 5L15 8"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</g>
						</svg>
					</label>
				</fieldset>
			</div>
		</div>

		<div class="flex justify-between">
			<button
				type="submit"
				class="btn btn-primary w-1/3"
				onclick={async () => {
					results = await filterSort.submit()
				}}
				disabled={filterSort.editing_indices.length > 0}
				bind:this={submitButton}
			>
				Screen Movies {#if !filterSort.changed}
					(changed)
				{/if}
			</button>

			<button class="btn btn-primary" onclick={() => imageModal?.showModal()}>
				Screener Image
			</button>
		</div>
	</form>
	<!-- Open the modal using ID.showModal() method -->
	<dialog bind:this={imageModal} class="modal w-full">
		<div class="modal-box flex w-full flex-col items-center justify-between">
			<ScreenerImageWrapper {filterSort} {results} />
		</div>
		<form method="dialog" class="modal-backdrop">
			<button>close</button>
		</form>
	</dialog>

	{#if results}
		{@const filter_columns = filterSort.getDisplayColumns()}
		<h1>Screening Results ({results?.screener_view.length})</h1>
		<table class="table">
			<thead>
				<tr>
					<th>Title</th>
					{#each filter_columns as filter}
						<th>{filter_name_to_title(filter.name)}</th>
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each results?.screener_view as movie}
					<tr>
						<td>
							<a href={`/m/${movie.movie_id}`}>{movie.title}</a>
						</td>
						{#each filter_columns as filter}
							<td>
								<!-- check if number and then add commas if big -->
								{#if dollar_names.includes(filter.name)}
									${formatKMB(movie[filter.name], 2)}
								{:else if typeof movie[filter.name] === 'number'}
									{movie[filter.name].toLocaleString('en-US', {
										maximumFractionDigits: 2
									})}
								{:else if filter.type === 'date'}
									{new Date(movie[filter.name]).toLocaleDateString()}
								{:else}
									{movie[filter.name] ?? 'N/A'}
								{/if}
							</td>
						{/each}
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</div>
