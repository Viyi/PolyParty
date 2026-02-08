<script lang="ts">
	import { onMount } from 'svelte';
	import { getUsersUsersGet } from '../../client';
	import type { UserRead } from '../../client';

	export let user_icon: string | undefined;
	export let username: string;
	export let balance: number;

	let failed = false;

	// let users = $state<UserRead[]>([]);
	// let loading = $state(true);

	// onMount(async () => {
	// 	try {
	// 		const res = await getUsersUsersGet();
	// 		if (res.data) {
	// 			users = res.data.sort((a, b) => (b.balance ?? 0) - (a.balance ?? 0));
	// 		}
	// 	} finally {
	// 		loading = false;
	// 	}
	// });
</script>

<div class="icon-container">
	{#if !failed  && user_icon}
		<img src={user_icon} on:error={() => (failed = true)} alt="hallo">
	{:else}
		<div class="placeholder-circle">
			{username.charAt(0).toUpperCase()}
		</div>
	{/if}
</div>

<style>
	/* This forces the SVG to actually take up space */
	.icon-container {
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 8px;
		overflow: hidden;
		background-color: oklch(var(--b2)); /* DaisyUI base-200 color */
	}

	.icon-container img {
		width: 100%;
		height: 100%;
		display: block;
		object-fit: cover;
	}

	.placeholder-circle {
		font-weight: bold;
		width: 85%;
		height: 85%;
		opacity: 0.5;
		outline: 2px white solid;
		text-align: center;
		display: flex;
		justify-content: center;
		align-items: center;
	}
</style>
