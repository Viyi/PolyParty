<script>
    import { goto } from "$app/navigation";

    let username = ''
    let password = ''

    async function login() {
        try{
            const response = await fetch('http://10.0.0.165:8051/auth/login',{
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({username: username, password: password})}
            )

            if (!response.ok) {
                throw new Error('login failed')
            }

            const data = await response.json();e
            console.log(data)
        } catch(err){
            console.error(err)
        }

    }
</script>

<div style="width: 100vw; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 8px">
    <div style="width: 30%; display: flex; flex-direction: column; justify-content: start; align-items: start; gap: 8px">
        <h1>Login</h1>
        <label>Username</label>
        <input bind:value={username} style="max-width: 200px; min-width: 200px;">
        <label>Password</label>
        <input bind:value={password} style="max-width: 200px; min-width: 200px;">
        <button on:click={login} style="max-width: 200px; min-width: 200px;">Login</button>
    </div>
</div>