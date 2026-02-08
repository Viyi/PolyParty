<script lang="ts">
	import { onMount } from 'svelte';
	import { getEventsEventsGet, getUserUsersCurrentGet } from '../../client';
	// Ensure you import the type that includes outcomes (EventReadWithShares)
	// or extend the generated Event type.
	import {
		type EventReadWithShares as dbEvent,
		closeEventEventsEventIdClosePost
	} from '../../client';

	async function handleCloseEvent(eventId: string, outcomeValue: number) {
		if (!confirm('Are you sure you want to close this event and pay out winners?')) return;

		try {
			// Using the endpoint you created earlier
			const res = await closeEventEventsEventIdClosePost({
				path: { event_id: eventId },
				body: { winning_value: outcomeValue }
			});

			if (res.data) {
				// Update local state so the badge turns red immediately
				events = events.map((ev) => (ev.id === eventId ? { ...ev, finalized: true } : ev));
				alert(`Event closed! Shares paid: ${res.data.shares_paid}`);
			}
		} catch (err) {
			console.error(err);
			alert('Failed to close event.');
		}
	}
	let events = $state<dbEvent[]>([]);
	let loading = $state(true);
	let admin = $state(false);
	onMount(async () => {
		try {
			const res = await getEventsEventsGet();
			if (res.data) {
				events = res.data;
			}

			const userRes = await getUserUsersCurrentGet();
			if (userRes.data) {
				admin = userRes.data.admin;
			}
		} finally {
			loading = false;
		}
	});

	let now = $state(Date.now());

	onMount(() => {
		const interval = setInterval(() => {
			now = Date.now();
		}, 600 * 10); // 60,000ms = 1 minute

		return () => clearInterval(interval); // Cleanup on destroy
	});

	function getRelativeTime(startTime: string, endTime: string) {
		let start = Date.parse(startTime);
		let target;
		if (start > now) {
			target = start;
		} else {
			target = Date.parse(endTime);
		}
		const diff = target - now;
		const isPast = diff < 0;
		const absDiff = Math.abs(diff);

		// Time calculations
		const days = Math.floor(absDiff / (1000 * 60 * 60 * 24));
		const hours = Math.floor((absDiff / (1000 * 60 * 60)) % 24);
		const mins = Math.floor((absDiff / (1000 * 60)) % 60);
		const secs = Math.floor((absDiff / 1000) % 60);

		// Helper to pad numbers to 2 digits
		const pad = (num: number) => String(num).padStart(2, '0');

		let timeStr = '';

		if (days > 0) {
			// We usually don't pad days, but we pad the units following it
			timeStr = `${days}d ${pad(hours)}h ${pad(mins)}m`;
		} else if (hours > 0) {
			timeStr = `${hours}h ${pad(mins)}m ${pad(secs)}s`;
		} else if (mins > 0) {
			timeStr = `${pad(mins)}m ${pad(secs)}s`;
		} else {
			timeStr = `${pad(secs)}s`;
		}

		return isPast ? `${timeStr} ago` : `${timeStr} left`;
	}

	let dialog;
	let isOpen = false;
	let currentEvent = $state<undefined | dbEvent>(undefined);

	let modalRef = $state<HTMLDialogElement>();

	// Watch the isOpen state and call the native methods
	$effect(() => {
		if (isOpen) {
			modalRef?.showModal();
		} else {
			modalRef?.close();
		}
	});

	import CreateEventModal from '../components/CreateEvent.svelte';

	let createModal = $state<ReturnType<typeof CreateEventModal>>();

	function handleEventCreated(newEvent: dbEvent) {
		events = [newEvent, ...events];
	}
</script>

<div class="p-4 w-full overflow-x-auto">
	<h2 class="text-2xl font-bold mb-4">Events</h2>
	<div class="p-4 w-full overflow-x-auto">
		<div class="mb-6 flex items-center justify-between">
			{#if admin}
				<button class="btn btn-primary btn-sm" onclick={() => createModal.show()}>
					+ New Event
				</button>
			{/if}
		</div>

		<CreateEventModal bind:this={createModal} onSuccess={handleEventCreated} />
	</div>

	{#if loading}
		<span class="loading loading-dots loading-lg"></span>
	{:else}
		<table class="table w-full">
			<thead>
				<tr>
					<th>Event</th>
					<th>Description</th>
					<th>Type</th>
					<th>Potential Outcomes</th>
					<th>Cutoff</th>
					<th>Status</th>
					{#if admin}
						<th>Admin</th>
					{/if}
				</tr>
			</thead>
			<tbody>
				{#each events as e (e.id)}
					<tr class="hover:bg-base-200/50 transition-colors">
						<td>
							<div class="font-bold">{e.title}</div>
							<div class="text-xs opacity-50">{e.id.slice(0, 8)}...</div>
						</td>
						<td>{e.description}</td>
						<td>
							<span class="badge badge-ghost text-xs uppercase">{e.type}</span>
						</td>
						<td>
							<div class="gap-2 max-w-xs flex w-full flex-col">
								{#each e.outcomes as outcome}
									<div
										class="gap-4 py-1 border-base-content/5 flex items-center justify-between border-b last:border-0"
									>
										<span class="text-sm font-medium">
											{#if e.finalized && e.value == outcome.value}
												✅
											{/if}
											{outcome.description}
										</span>

										<span class="text-xs font-mono text-success tabular-nums">
											{Math.round(outcome.cost * 100)}%
										</span>
									</div>
								{/each}
							</div>
						</td>
						<td>
							{getRelativeTime(e.start_time, e.end_time)}
						</td>
						<td>
							{#if e.finalized}
								<span class="badge badge-error">Closed</span>
							{:else}
								<span class="badge badge-success">Open</span>
							{/if}
						</td>
						{#if admin}
							<td>
								{#if e.finalized}
									<button class="btn btn-disabled btn-xs">Finalized</button>
								{:else}
									<div class="join border-base-content/10 border">
										<select
											class="select select-bordered select-xs join-item focus:outline-none"
											onchange={(el) => {
												const val = parseInt(el.currentTarget.value);
												if (!isNaN(val)) handleCloseEvent(e.id, val);
											}}
										>
											<option disabled selected>Pick Winner</option>
											{#each e.outcomes as outcome}
												<option value={outcome.value}>
													{outcome.description}
												</option>
											{/each}
										</select>
									</div>
								{/if}
							</td>
						{/if}
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</div>
