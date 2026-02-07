<script lang="ts">
	import { onMount } from 'svelte';
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import ThemeDropdown from '$lib/components/ThemeDropdown.svelte';

	import { client } from '../client/client.gen';
	import { API_HOST } from '../conts';

	let { children } = $props();
	let isReady = $state(false);

	onMount(() => {
		// 1. Pull the token from storage
		const token = localStorage.getItem('access_token');

		// 2. Configure the client with the token if it exists
		client.setConfig({
			baseUrl: API_HOST,
			headers: {
				// Only add the header if we actually have a token
				...(token && { Authorization: `Bearer ${token}` })
			}
		});

		// 3. Mark the app as initialized so we can render children
		isReady = true;
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<nav>
	<ThemeDropdown />
</nav>

{#if isReady}
	{@render children()}
{:else}
	<div class="loading-overlay">
		<p>Initializing session...</p>
	</div>
{/if}

<style>
	.loading-overlay {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 100vh;
		font-family: sans-serif;
	}
</style>
