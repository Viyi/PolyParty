<script lang="ts">
	import { onMount } from 'svelte';
	import { getUsersUsersGet } from '../../client';
	import type { UserRead } from '../../client';
	import UserIcon from './UserIcon.svelte';

	let user: UserRead

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

<div>
	<UserIcon />
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
		opacity: 0.5;
	}
</style>
