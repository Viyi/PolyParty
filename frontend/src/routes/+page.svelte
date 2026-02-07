<script>
    import { goto } from "$app/navigation";
</script>

<div style="width: 100vw; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 8px">
    <h1>Welcome to Poly Party</h1>
    <button on:click={() => goto("/login")} style="max-width: 200px; min-width: 200px;">Login</button>
    <button on:click={() => goto("/register")} style="max-width: 200px; min-width: 200px;">Register</button>
</div>