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

            const data = await response.json();
            console.log(data)
        } catch(err){
            console.error(err)
        }

    }
</script>

<div style="width: 100vw; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 8px">
    <div style="width: 30%; display: flex; flex-direction: column; justify-content: start; align-items: start; gap: 8px">
        <h1>User Page</h1>
    </div>
</div>