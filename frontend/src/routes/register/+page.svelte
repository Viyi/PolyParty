<script>
    import { goto } from "$app/navigation";
    import "../../app.css"
	import { API_HOST } from "../../conts";

    let username = ''
    let password = ''
    let user_id = null

    async function login() {
        try{
            const response = await fetch(`${API_HOST}/auth/register`,{
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({username: username, balance: 100, password: password})}
            )

            if (!response.ok) {
                throw new Error('login failed')
            }

            const data = await response.json();
            console.log(data)
            user_id = data.balance
            localStorage.setItem("access_token", data.access_token); // assuming FastAPI returns access_token
            localStorage.setItem("user_id", data.user_id); // or data.id depending on backend
            goto(`/user/`)
        } catch(err){
            console.error(err)
        }

    }
</script>

<div class="parent-container">
    <div class="parent-subcontainer">
        <div class="title-container">
            <button class="back-btn" on:click={() => goto('/')}>back</button>
            <h1 class="title">Register</h1>
        </div>
        <label>Username</label>
        <input bind:value={username} style="max-width: 200px; min-width: 200px;">
        <label>Password</label>
        <input bind:value={password} style="max-width: 200px; min-width: 200px;">
        <button on:click={login} style="max-width: 200px; min-width: 200px;">Login</button>
    </div>
</div>