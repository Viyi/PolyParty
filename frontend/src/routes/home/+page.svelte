<script lang="ts">
	import { onMount } from 'svelte';
	import { getEventsEventsGet, getUsersUsersGet } from '../../client';
	import type { Event, UserRead } from '../../client';
	import LeaderboardTable from '$lib/components/LeaderboardTable.svelte';
	import EventTable from '$lib/components/EventTable.svelte';

	let events = $state<Event[]>([]);
	let users = $state<UserRead[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			const [eventsRes, usersRes] = await Promise.all([getEventsEventsGet(), getUsersUsersGet()]);

			if (eventsRes.data) events = eventsRes.data;

			if (usersRes.data) {
				users = usersRes.data.sort((a, b) => (b.balance ?? 0) - (a.balance ?? 0));
			}
		} catch (err) {
			console.error('Failed to load data:', err);
			error = 'Failed to load dashboard data.';
		} finally {
			loading = false;
		}
	});

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<div class="gap-4 p-4 auto-rows grid grid-cols-3">
	<div class="card bg-base-200 shadow-lg col-span-2 row-span-2 border-1">
		<div class="card-body">
			<EventTable />
		</div>
	</div>

	<div class="card bg-base-200 shadow-lg border-1">
		<div class="card-body items-center text-center">
			<LeaderboardTable />
		</div>
	</div>
</div>
