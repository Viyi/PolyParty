<script lang="ts">
	import { onMount } from 'svelte';
	import { getUsersUsersGet } from '../../client';
	import type { UserRead } from '../../client';

	let users = $state<UserRead[]>([]);
	let loading = $state(true);

	onMount(async () => {
		try {
			const res = await getUsersUsersGet();
			if (res.data) {
				users = res.data.sort((a, b) => (b.balance ?? 0) - (a.balance ?? 0));
			}
		} finally {
			loading = false;
		}
	});
</script>

<div class="w-full overflow-x-auto">
	<h2>Leaderboard</h2>
	<table class="table">
		<thead>
			<tr>
				<th class="w-20">Icon</th>
				<th>Username</th>
				<th>Balance</th>
			</tr>
		</thead>
		<tbody>
			{#each users as user, i (user.id)}
				<tr class="hover:bg-base-200/50 transition-colors">
					<td>
						<div class="icon-container">
							{#if user.icon_url}
								<img src={user.icon_url} alt="Avatar" loading="lazy" />
							{:else}
								<div class="placeholder-circle">
									{user.username.charAt(0).toUpperCase()}
								</div>
							{/if}
						</div>
					</td>
					<td class="font-bold">{user.username}</td>
					<td>
						<span class="text-success font-mono">
							${user.balance?.toLocaleString() ?? 0}
						</span>
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
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
