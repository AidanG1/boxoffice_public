<script lang="ts">
	import { themeState } from '$lib/themes.svelte'

	const light_themes = ['jaws', 'paddington', 'three-idiots', 'kill-bill', 'a-clockwork-orange', 'grand-budapest-hotel']

	const dark_themes = ['godfather', 'blade-runner', 'scarface', 'boyhood', 'oldboy', 'inception']

	const setTheme = (theme: string, theme_type: 'light' | 'dark') => {
		themeState.theme = theme
		themeState.theme_type = theme_type
	}

	const theme_name_to_title = (theme: string) => {
		// title case, replace hyphens with spaces
		return theme
			.split('-')
			.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
			.join(' ')
	}
</script>

<svelte:head>
	<title>Settings - BoxOffice Insights</title>
	<meta name="description" content="Manage your settings for BoxOffice Insights." />
</svelte:head>

{#snippet themeButton(theme: string, theme_type: 'light' | 'dark')}
	<button onclick={() => setTheme(theme, theme_type)} class="mb-2" data-theme={theme}>
		<div
			class="bg-base-100 text-base-content border-primary w-full cursor-pointer border-2 font-sans"
		>
			<div class="grid grid-cols-5 grid-rows-3">
				<div class="bg-base-100 col-start-1 row-span-2 row-start-1"></div>
				<div class="bg-base-200 col-start-1 row-span-1 row-start-2"></div>
				<div class="bg-base-300 col-start-1 row-start-3"></div>
				<div
					class="bg-base-100 col-span-4 col-start-2 row-span-3 row-start-1 flex flex-col gap-1 p-2"
				>
					<div class="font-bold">{theme_name_to_title(theme)}</div>
					<div class="flex flex-wrap gap-1">
						<div
							class="bg-primary flex aspect-square w-5 items-center justify-center rounded lg:w-6"
						>
							<div class="text-primary-content text-sm font-bold">A</div>
						</div>
						<div
							class="bg-secondary flex aspect-square w-5 items-center justify-center rounded lg:w-6"
						>
							<div class="text-secondary-content text-sm font-bold">A</div>
						</div>
						<div
							class="bg-accent flex aspect-square w-5 items-center justify-center rounded lg:w-6"
						>
							<div class="text-accent-content text-sm font-bold">A</div>
						</div>
						<div
							class="bg-neutral flex aspect-square w-5 items-center justify-center rounded lg:w-6"
						>
							<div class="text-neutral-content text-sm font-bold">A</div>
						</div>
						<div class="bg-info flex aspect-square w-5 items-center justify-center rounded lg:w-6">
							<div class="text-info-content text-sm font-bold">A</div>
						</div>
						<div
							class="bg-success flex aspect-square w-5 items-center justify-center rounded lg:w-6"
						>
							<div class="text-success-content text-sm font-bold">A</div>
						</div>
						<div
							class="bg-warning flex aspect-square w-5 items-center justify-center rounded lg:w-6"
						>
							<div class="text-warning-content text-sm font-bold">A</div>
						</div>
						<div class="bg-error flex aspect-square w-5 items-center justify-center rounded lg:w-6">
							<div class="text-error-content text-sm font-bold">A</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</button>
{/snippet}

<div class="p-2">
	<h1>Settings</h1>

	<h2>Themes: using {theme_name_to_title(themeState.theme)} ({themeState.theme_type})</h2>

	<div class="mb-4">
		<div class="xs:grid-cols-1 grid gap-2 md:grid-cols-2 lg:grid-cols-3">
			{#each light_themes as theme}
				{@render themeButton(theme, 'light')}
			{/each}
		</div>
		<div class="xs:grid-cols-1 grid gap-2 md:grid-cols-2 lg:grid-cols-3">
			{#each dark_themes as theme}
				{@render themeButton(theme, 'dark')}
			{/each}
		</div>
	</div>
</div>
