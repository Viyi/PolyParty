<script>
  let selectedOutcome = null;
  let modalRef;

  function triggerBet(outcome) {
    selectedOutcome = outcome;
    modalRef.showModal();
  }
</script>

{#each outcomes as outcome}
  <button class="btn" on:click={() => triggerBet(outcome)}>
    Bet on {outcome.description}
  </button>
{/each}

<dialog bind:this={modalRef} class="modal">
  <div class="modal-box">
    {#if selectedOutcome}
      <h3 class="font-bold text-lg">Betting on: {selectedOutcome.description}</h3>
      <p>Current Price: ${selectedOutcome.cost.toFixed(2)}</p>
      {/if}
    
    <div class="modal-action">
      <form method="dialog">
        <button class="btn">Close</button>
      </form>
    </div>
  </div>
</dialog>