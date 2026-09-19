<script>
	import Navbar from '$lib/components/Navbar.svelte'
	import { initializeTheme, syncTheme, themeState } from '$lib/themes.svelte'
	import '../app.css'
	import { fade } from 'svelte/transition'
	import { cubicIn, cubicOut } from 'svelte/easing'

	let { data, children } = $props()

	import { onMount } from 'svelte'

	onMount(() => {
		initializeTheme()
	})

	$effect(() => {
		syncTheme(themeState)
	})
</script>

<svelte:head>
	<title>Reel Numbers</title>
	<meta name="description" content="Reel Numbers: track the domestic box office performance of movies." />
</svelte:head>

<Navbar />
{#key data.pathname}
	<div
		in:fade={{ easing: cubicOut, duration: 300, delay: 400 }}
		out:fade={{ easing: cubicIn, duration: 300 }}
	>
		{@render children()}
	</div>
{/key}
