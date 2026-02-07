<script>
    import { goto } from "$app/navigation";
    import "../../app.css"

    let username = ''
    let password = ''

    async function login() {
        try{
            const formData = new URLSearchParams()
            formData.append("username", username)
            formData.append("password", password)

            const response = await fetch('http://10.0.0.165:8051/auth/login',{
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: formData.toString()}
            )

            if (!response.ok) {
                throw new Error('login failed')
            }

            const data = await response.json();
            console.log(data)

             // Save JWT and user id
            localStorage.setItem("access_token", data.access_token); // assuming FastAPI returns access_token
            localStorage.setItem("user_id", data.user_id); // or data.id depending on backend
            goto("/user/")
        } catch(err){
            console.error(err)
        }

    }
</script>

<div class="parent-container">
    <div class="parent-subcontainer">
        <div class="title-container">
            <button class="back-btn" on:click={() => goto('/')}>back</button>
            <h1 class="title">Login</h1>
        </div>
        <label>Username</label>
        <input bind:value={username} style="max-width: 200px; min-width: 200px;">
        <label>Password</label>
        <input bind:value={password} style="max-width: 200px; min-width: 200px;">
        <button on:click={login} style="max-width: 200px; min-width: 200px;">Login</button>
    </div>
</div>