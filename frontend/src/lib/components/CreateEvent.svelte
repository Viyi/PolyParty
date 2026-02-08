<script lang="ts">
	import { createEventEventsCreatePost } from '../../client';
	import type { EventReadWithShares as dbEvent } from '../../client';

	// Props: onSuccess allows the parent to update the list immediately
	let { onSuccess } = $props<{ onSuccess: (event: dbEvent) => void }>();

	let modalRef = $state<HTMLDialogElement>();
	let isCreating = $state(false);

	const formatLocalISO = (date: Date) => {
		const offset = date.getTimezoneOffset() * 60000;
		const localISOTime = new Date(date.getTime() - offset).toISOString().slice(0, 16);
		return localISOTime;
	};

	const now = new Date();
	const tomorrow = new Date();
	tomorrow.setDate(now.getDate() + 1);

	let newEvent = $state({
		title: '',
		description: '',
		start_time: formatLocalISO(now),
		end_time: formatLocalISO(tomorrow),
		type: 'singleton',
		value: 1,
		outcomes: [
			{ description: '', value: 0 },
			{ description: '', value: 1 }
		]
	});

	// Validation logic
	let isValid = $derived(
		newEvent.title.length > 0 &&
			newEvent.start_time !== '' &&
			newEvent.end_time !== '' &&
			newEvent.outcomes.every((o) => o.description.length > 0)
	);

	export function show() {
		modalRef?.showModal();
	}

	function addOutcome() {
		newEvent.outcomes.push({ description: '', value: newEvent.outcomes.length });
	}

	function removeOutcome(index: number) {
		if (newEvent.outcomes.length > 1) {
			newEvent.outcomes = newEvent.outcomes.filter((_, i) => i !== index);
		}
	}

	async function submitCreateEvent() {
		isCreating = true;
		try {
			const res = await createEventEventsCreatePost({
				body: {
					...newEvent,
					start_time: new Date(newEvent.start_time).toISOString(),
					end_time: new Date(newEvent.end_time).toISOString(),
					outcomes: newEvent.outcomes.map((o) => ({ ...o }))
				}
			});
			if (res.data) {
				onSuccess(res.data as dbEvent);
				modalRef?.close();
				// Reset form logic...
			}
		} catch (err) {
			console.error(err);
			alert('Error creating event. Check console.');
		} finally {
			isCreating = false;
		}
	}
</script>

<dialog bind:this={modalRef} class="modal modal-bottom sm:modal-middle">
	<div class="modal-box max-w-2xl border-base-content/10 w-11/12 border">
		<h3 class="text-lg font-bold">Create New Event</h3>

		<div class="mt-4 gap-4 md:grid-cols-2 grid grid-cols-1">
			<label class="form-control w-full">
				<div class="label"><span class="label-text">Title</span></div>
				<input
					type="text"
					bind:value={newEvent.title}
					class="input input-bordered"
					placeholder="Event Name"
				/>
			</label>
			<label class="form-control w-full">
				<div class="label"><span class="label-text">Description</span></div>
				<input
					type="text"
					bind:value={newEvent.description}
					class="input input-bordered"
					placeholder="Description of event"
				/>
			</label>

			<label class="form-control w-full">
				<div class="label"><span class="label-text">Type</span></div>
				<select class="select select-bordered" bind:value={newEvent.type}>
					<option value="singleton">Singleton</option>

					<option value="multiple-choice">Multiple Choice</option>
					<option value="over/under">Over/Under</option>
				</select>
			</label>

			<label class="form-control w-full">
				<div class="label"><span class="label-text">Start Time</span></div>
				<input
					type="datetime-local"
					bind:value={newEvent.start_time}
					class="input input-bordered"
				/>
			</label>

			<label class="form-control w-full">
				<div class="label"><span class="label-text">End Time</span></div>
				<input type="datetime-local" bind:value={newEvent.end_time} class="input input-bordered" />
			</label>
		</div>

		<div class="divider text-xs tracking-widest uppercase opacity-50">Outcomes</div>

		<div class="space-y-2">
			{#each newEvent.outcomes as outcome, i}
				<div class="gap-2 flex items-center">
					<input
						type="text"
						bind:value={outcome.description}
						placeholder="Outcome Description"
						class="input input-bordered input-sm flex-1"
					/>
					<input
						type="number"
						bind:value={outcome.value}
						class="input input-bordered input-sm w-20"
					/>
					<button
						class="btn btn-ghost btn-sm btn-square"
						onclick={() => removeOutcome(i)}
						disabled={newEvent.outcomes.length <= 1}>✕</button
					>
				</div>
			{/each}
		</div>

		<button class="btn btn-ghost btn-sm mt-4 w-full border-dashed" onclick={addOutcome}
			>+ Add Outcome</button
		>

		<div class="modal-action">
			<form method="dialog">
				<button class="btn">Cancel</button>
			</form>
			<button class="btn btn-primary" disabled={!isValid || isCreating} onclick={submitCreateEvent}>
				{#if isCreating}<span class="loading loading-spinner"></span>{/if}
				Create Event
			</button>
		</div>
	</div>
	<form method="dialog" class="modal-backdrop">
		<button>close</button>
	</form>
</dialog>
