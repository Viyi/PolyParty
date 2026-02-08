<script lang="ts">
	import type { Event as dbEvent } from '../../client';

	// Svelte 5 Props
	let {
		event
	}: {
		event: dbEvent | null;
	} = $props();

	let dialogRef = $state<HTMLDialogElement>();
	let quantity = $state(1);

	// Helper to find the description of an outcome for the shares list
	const getOutcomeName = (outcomeId: string) => {
		return event?.outcomes.find((o) => o.id === outcomeId)?.description ?? 'Unknown Outcome';
	};

	console.log(event.target);
</script>

{#if event}
	<div class="modal-box max-w-2xl border-base-300 shadow-2xl border">
		<button onclick={close} class="btn btn-sm btn-circle btn-ghost right-2 top-2 absolute">✕</button
		>

		<header class="mb-6">
			<h3 class="text-2xl font-black tracking-tighter uppercase italic">
				{event.title}
			</h3>
			<p class="text-sm opacity-70">{event.description}</p>
		</header>

		<section class="mb-8">
			<h4 class="text-xs font-bold mb-3 tracking-widest uppercase opacity-50">Select Outcome</h4>
			<div class="gap-3 grid grid-cols-1">
				{#each event.outcomes as outcome}
					<button
						class="group p-4 rounded-xl border-base-300 hover:border-primary bg-base-100 flex items-center justify-between border-2 text-left transition-all"
						onclick={() => console.log('Bet placed on:', outcome.id, 'Quantity:', quantity)}
					>
						<div>
							<span class="font-bold block">{outcome.description}</span>
							<span class="text-xs opacity-60">Price per share: ${outcome.cost}</span>
						</div>
						<div class="gap-4 flex items-center">
							<span class="text-xl font-mono font-black text-primary">
								{Math.round(outcome.cost * 100)}%
							</span>
							<div
								class="btn btn-primary btn-sm px-6 opacity-0 transition-opacity group-hover:opacity-100"
							>
								BUY
							</div>
						</div>
					</button>
				{/each}
			</div>

			<div class="mt-4 gap-4 p-4 bg-base-200 rounded-lg flex items-center">
				<label for="qty" class="text-sm font-bold">Quantity:</label>
				<input
					id="qty"
					type="number"
					bind:value={quantity}
					min="1"
					class="input input-bordered input-sm w-20"
				/>
				<span class="text-xs italic opacity-50">Total value: ${event.value * quantity}</span>
			</div>
		</section>

		<section>
			<h4 class="text-xs font-bold mb-3 tracking-widest uppercase opacity-50">
				Your Purchased Shares
			</h4>
			<div class="bg-base-300/30 rounded-xl overflow-hidden">
				<div class="max-h-48 p-2 space-y-2 overflow-y-auto">
					{#if event.shares.length === 0}
						<div class="p-8 text-sm text-center italic opacity-30">No shares owned yet</div>
					{:else}
						{#each event.shares as share}
							<div
								class="bg-base-100 p-3 rounded-lg border-base-content/5 shadow-sm flex items-center justify-between border"
							>
								<div class="flex flex-col">
									<span class="text-xs font-bold">{getOutcomeName(share.outcome_id)}</span>
									<span class="font-mono text-[10px] opacity-50"
										>{new Date(share.timestamp).toLocaleString()}</span
									>
								</div>
								<div class="gap-3 flex items-center">
									<div class="text-right">
										<div class="text-xs font-bold">${share.wager}</div>
										<div class="tracking-tighter text-[9px] uppercase opacity-50">Wager</div>
									</div>
									<div class="badge badge-outline badge-sm font-mono opacity-50">
										{share.id.slice(-6)}
									</div>
								</div>
							</div>
						{/each}
					{/if}
				</div>
			</div>
		</section>

		<div class="modal-action">
			<button onclick={close} class="btn btn-ghost">Cancel</button>
		</div>
	</div>
{/if}

<style>
	/* Ensure the scrollbar doesn't look clunky */
	.overflow-y-auto::-webkit-scrollbar {
		width: 4px;
	}
	.overflow-y-auto::-webkit-scrollbar-thumb {
		background: hsl(var(--bc) / 0.2);
		border-radius: 10px;
	}
</style>
