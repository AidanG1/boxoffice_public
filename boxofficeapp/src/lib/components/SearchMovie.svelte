<script lang="ts">
	import { searchMovie, type MovieSearchResult } from '$lib/utils'

	let {
		select_function = (result: MovieSearchResult) => {
			// Default select function, can be overridden
			console.log('Selected movie:', result)
		},
		placeholder = 'Search for a movie...',
		clear_results = false,
		respond_to_command_slash = false
	}: {
		select_function?: (result: MovieSearchResult) => void
		placeholder?: string
		clear_results?: boolean
		respond_to_command_slash?: boolean
	} = $props()

	let searchQuery: string = $state('')
	let debouncedQuery: string = $state('')
	let results: MovieSearchResult[] = $state([])
	let force_closed = $state(false)
	let searchInput: HTMLInputElement | null = $state(null)

	$effect(() => {
		if (searchQuery.length < 2) {
			debouncedQuery = ''
			results = []
			return
		}

		// Debounce the search query
		const timeout = setTimeout(() => {
			debouncedQuery = searchQuery
		}, 300)
	})

	$effect(() => {
		if (debouncedQuery) {
			searchMovie(debouncedQuery).then((res) => {
				results = res
			})
		} else {
			results = []
		}
	})
</script>

<svelte:window
	on:keyup={(e) => {
		if (e.key === 'Escape') {
			force_closed = true
		}
		if (e.key === 'Enter' && results.length > 0) {
			// Select the first result on Enter
			select_function(results[0])
			force_closed = true
			if (clear_results) {
				searchQuery = ''
				results = []
			}
		}
		// if command slash is pressed, focus the input
		if (respond_to_command_slash && e.ctrlKey && e.key === '/') {
			e.preventDefault()
			force_closed = false
			searchInput?.focus()
		}
	}}
/>

<details class="dropdown" open={results.length > 0 && !force_closed}>
	<summary class="list-none">
		<label class="input w-48">
			<input
				type="text"
				{placeholder}
				bind:this={searchInput}
				bind:value={searchQuery}
				class="focus:ring-primary grow"
				onfocus={() => (force_closed = false)}
				oninput={() => (force_closed = false)}
			/>
			<button
				class="btn btn-sm btn-circle border-0"
				onclick={() => {
					debouncedQuery = ''
					searchQuery = ''
					results = []
				}}
				aria-label="Clear search"
				tabindex={results.length + 1}
			>
				<span>&times;</span>
			</button>
		</label>
	</summary>
	<ul class="menu dropdown-content rounded-box bg-base-100 z-1 w-52 border p-2 shadow-sm">
		{#each results as result, index}
			<li>
				<button
					onclick={() => {
						select_function(result)
						force_closed = true
						if (clear_results) {
							searchQuery = ''
							results = []
						}
					}}
					tabindex={index + 1}
					class="focus:border-primary focus:border"
				>
					{result.title} ({result.release_date ? result.release_date.slice(0, 4) : 'N/A'})
				</button>
			</li>
		{/each}
	</ul>
</details>
