<script lang="ts">
	import { onMount } from 'svelte';
	import { getUsersUsersGet, type UserRead } from '../../client';

	// 1. Initialize reactive state
	let users = $state<UserRead[]>([]);
	let loading = $state(true);

	onMount(async () => {
		const token = localStorage.getItem('access_token');

		if (!token) {
			// If no token, stop everything and kick them to login
			goto('/login');
			return;
		}
		// 2. Await the response
		const { data, error } = await getUsersUsersGet();

		if (data) {
			users = data;
		} else if (error) {
			console.error('Failed to load users:', error);
		}
		loading = false;
	});
</script>

{#if loading}
	<p>Loading users...</p>
{:else}
	<table>
		<thead>
			<tr>
				<th>ID</th>
				<th>Username</th>
				<th>Balance</th>
			</tr>
		</thead>
		<tbody>
			{#each users as user}
				<tr>
					<td>{user.id}</td>
					<td>{user.username}</td>
					<td>${user.balance.toFixed(2)}</td>
				</tr>
			{/each}
		</tbody>
	</table>
{/if}

<style>
	table {
		width: 100%;
		border-collapse: collapse;
	}
	th,
	td {
		border: 1px solid #ddd;
		padding: 8px;
		text-align: left;
	}
	th {
		background-color: #f4f4f4;
	}
</style>
