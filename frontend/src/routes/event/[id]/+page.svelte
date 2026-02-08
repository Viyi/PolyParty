<script lang="ts">
	import { onMount } from 'svelte';
	import { getEventDetailsEventsEventIdGet, getEventsEventsGet } from '../../../client';
    import { page } from '$app/stores';

	// Ensure you import the type that includes outcomes (EventReadWithShares)
	// or extend the generated Event type.
	import type { EventReadWithShares as dbEvent } from '../../../client';
    import { goto } from "$app/navigation";
	import { setAuthParams } from '../../../client/client/utils.gen';

	let event = $state<dbEvent>();
	let loading = $state(true);

    const pageSlug = $page.params.id

	onMount(async () => {
        console.log(pageSlug)
		try {
			const res = await getEventDetailsEventsEventIdGet({path:{event_id: pageSlug}});
			if (res.data) {
				console.log(res.data)
				event = res.data;
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

	const openEvent = (event_id: string) => {
		goto(`/event/${event_id}`)
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
</script>

<div class="p-4 w-full overflow-x-auto">
	<h2 class="text-2xl font-bold mb-0">{event?.title}</h2>
	<div class="text-xs opacity-50 mb-8">{event?.description}</div>

	{#if loading || !event}
		<span class="loading loading-dots loading-lg"></span>
	{:else}
		<table class="table w-full">
			<thead>
				<tr>
					<th>` `</th>
					<th>Type</th>
					<th>Potential Outcomes</th>
					<th>Cutoff</th>
					<th>Status</th>
				</tr>
			</thead>
			<tbody>
					<tr class="hover:bg-base-200/50 transition-colors">
						<td>{event.description}</td>
						<td>
							<span class="badge badge-ghost text-xs uppercase">{event.type}</span>
						</td>
						<td>
							<div class="gap-2 max-w-xs flex w-full flex-col">
								{#each event.outcomes as outcome}
									<div
										class="gap-4 py-1 border-base-content/5 flex items-center justify-between border-b last:border-0"
									>
										<span class="text-sm font-medium">
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
							{getRelativeTime(event.start_time, event.end_time)}
						</td>
						<td>
							{#if event.finalized}
								<span class="badge badge-error">Closed</span>
							{:else}
								<span class="badge badge-success">Open</span>
							{/if}
						</td>
					</tr>
			</tbody>
		</table>
	{/if}
</div>
