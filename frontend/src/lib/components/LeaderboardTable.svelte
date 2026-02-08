<script lang="ts">
	import { onMount } from 'svelte';
	import { getUsersUsersGet } from '../../client';
	import type { UserRead } from '../../client';
	import UserIcon from './UserIcon.svelte';

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
						<UserIcon user_icon={user.icon_url} balance={user.balance ? user.balance : 0} username={user.username}/>
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
