<script lang="ts">
	import { onMount } from 'svelte';
	import { getEventsEventsGet, getUsersUsersGet } from '../../client';
	import type { Event, UserRead } from '../../client';

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

<div class="p-6 max-w-7xl space-y-8 mx-auto">
	<header
		class="md:flex-row gap-4 bg-base-200 p-6 rounded-box shadow-sm flex flex-col items-center justify-between"
	>
		<div class="gap-3 flex items-center">
			<div class="text-4xl">🎲</div>
			<h1 class="text-3xl font-black tracking-tight">Poly Party</h1>
		</div>
		<div class="join">
			<a href="/debug" class="btn btn-outline btn-secondary join-item">🛠 Debug</a>
			<a href="/user" class="btn btn-primary join-item">👤 User Profile</a>
		</div>
	</header>

	{#if error}
		<div class="alert alert-error shadow-lg">
			<span>{error}</span>
		</div>
	{/if}

	{#if loading}
		<div class="py-20 gap-4 flex flex-col items-center justify-center">
			<span class="loading loading-dots loading-lg text-primary"></span>
			<p class="text-base-content/60 font-medium italic">Syncing with the markets...</p>
		</div>
	{:else}
		<div class="lg:grid-cols-3 gap-8 grid grid-cols-1">
			<section class="lg:col-span-2 space-y-4">
				<div class="flex items-center justify-between">
					<h2 class="text-2xl font-bold px-2">Active Events</h2>
					<span class="badge badge-neutral">{events.length} Markets</span>
				</div>

				<div class="card bg-base-100 shadow-xl border-base-300 border">
					<div class="overflow-x-auto">
						<table class="table-zebra table w-full">
							<thead>
								<tr class="text-base-content/70">
									<th>Title</th>
									<th>Type</th>
									<th>Value</th>
									<th>Ends At</th>
									<th>Status</th>
								</tr>
							</thead>
							<tbody>
								{#each events as event}
									<tr class="hover">
										<td class="font-bold text-primary">{event.title}</td>
										<td>
											<span class="badge badge-sm badge-ghost font-semibold text-xs uppercase"
												>{event.type}</span
											>
										</td>
										<td class="font-mono">{event.value}</td>
										<td class="text-xs text-base-content/60">{formatDate(event.end_time)}</td>
										<td>
											{#if event.finalized}
												<div class="badge badge-error badge-outline gap-1">Closed</div>
											{:else}
												<div class="badge badge-success gap-1">Open</div>
											{/if}
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
					{#if events.length === 0}
						<div class="p-10 text-base-content/40 text-center">No active events found.</div>
					{/if}
				</div>
			</section>

			<section class="lg:col-span-1 space-y-4">
				<h2 class="text-2xl font-bold px-2">Leaderboard 🏆</h2>
				<div class="card bg-base-100 shadow-xl border-base-300 h-fit border">
					<div class="card-body p-0">
						<ul class="divide-base-200 divide-y">
							{#each users as user, index}
								<li
									class="p-4 hover:bg-base-200 first:rounded-t-box last:rounded-b-box flex items-center justify-between transition-colors"
								>
									<div class="gap-3 flex items-center">
										<span class="w-6 font-bold text-base-content/40 text-sm text-center"
											>#{index + 1}</span
										>

										<div class="avatar {index === 0 ? 'online' : ''}">
											<div
												class="w-10 ring-primary ring-offset-base-100 rounded-full ring ring-offset-2"
											>
												{#if user.icon_url}
													<img src={user.icon_url} alt={user.username} />
												{:else}
													<div
														class="bg-neutral text-neutral-content grid h-full w-full place-items-center"
													>
														<span>{user.username[0].toUpperCase()}</span>
													</div>
												{/if}
											</div>
										</div>

										<span class="font-semibold text-sm">{user.username}</span>
									</div>

									<div class="font-mono font-bold text-success text-sm">
										${(user.balance ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
									</div>
								</li>
							{/each}
						</ul>
					</div>
				</div>
			</section>
		</div>
	{/if}
</div>
