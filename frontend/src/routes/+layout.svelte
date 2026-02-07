<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import ThemeDropdown from '$lib/components/ThemeDropdown.svelte';

	let { children } = $props();
</script>
<nav><ThemeDropdown></ThemeDropdown></nav>
<svelte:head><link rel="icon" href={favicon} /></svelte:head>
{@render children()}
