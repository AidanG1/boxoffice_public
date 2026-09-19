<script lang="ts">
	import { tmdb_path_to_url } from '$lib/utils'

	let { data } = $props()

	const colorful_jobs = [
		'Director',
		'Director of Photography',
		'Original Music Composer',
	];

	const get_color_by_credit_order = (credit_order: number | null, credit_job: string): string => {
		if (credit_order === null) {
			if (colorful_jobs.includes(credit_job)) return 'bg-warning/50'
			return 'bg-neutral/50'
		}
		if (credit_order < 5) return 'bg-success/50'
		return 'bg-info/50'
	}
</script>

{#snippet credits_table()}
	<div class="mt-2">
		<h2 class="text-lg font-semibold">U.S. Theatrical Release Credits</h2>
		<table class="table w-full">
			<thead>
				<tr>
					<th>Movie</th>
					<th>Role or Job</th>
					<th>Credit Order</th>
					<th>Year</th>
				</tr>
			</thead>
			<tbody>
				{#each data.person.castorcrew as credit}
					<tr class={get_color_by_credit_order(credit.credit_order, credit.job)}>
						<td><a href={`/m/${credit.movie_id}`}>{credit.movie.title}</a></td>
						<td>{credit.character_name || credit.job || 'N/A'}</td>
						<td>{credit.credit_order !== null ? credit.credit_order + 1 : 'N/A'}</td>
						<td>{new Date(credit.movie.release_date).getFullYear()}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/snippet}

<div class="p-2">
	<!-- person image -->
	<div class="mb-4 flex gap-4">
		<img
			src={tmdb_path_to_url(data.person.profile_path || '')}
			alt={data.person.name}
			class="h-64 rounded-md"
		/>
		<div class="w-full">
			<div class="flex flex-col md:flex-row w-full gap-4">
				<h1 class="grow">
					{data.person.name}
				</h1>
				<p>
					<a
						href={`https://www.themoviedb.org/person/${data.person.tmdb_id}`}
						class="flex gap-1"
						target="_blank"
					>
						View on TMDB <img src="/logos/tmdb.svg" alt="TMDB" class="m-1 h-6" />
					</a>
				</p>
			</div>
			<!-- now credits -->
			<div class="hidden md:block">
				{@render credits_table()}
			</div>
		</div>
	</div>
	<!-- now credits -->
	<div class="block md:hidden">
		{@render credits_table()}
	</div>
</div>
