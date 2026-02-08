<script>
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import "../../app.css"
	import { API_HOST } from "../../conts";
	import { client } from '../../client/client.gen';
    import { getUserUsersCurrentGet } from "../../client";


    let username = ''
    let password = ''
    let user_id = null
    let admin = false
    let token = null

    const pib1 = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%2Fid%2FOIP.pVwLWcMokx49OUsH73TEZwHaGJ%3Fpid%3DApi&f=1&ipt=514c01055b26b842f1dec963e71778674eb06cdb6d48f6803f6b04e96bb2ea25&ipo=images"
    const pib2 = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fmedia1.tenor.com%2Fm%2FFhms4-y8QDgAAAAd%2Fpibble-pibble-dog.gif&f=1&nofb=1&ipt=b212a81f20a875bda2857a6d5e3da978f1ae8b9e25c6978ff88170effdcd2ffd"


    onMount(async () => {
		try {
			const res = await getUserUsersCurrentGet()
			if (res.data) {
				// users = res.data.sort((a, b) => (b.balance ?? 0) - (a.balance ?? 0));
                admin = res.data.admin ? res.data.admin : false
			}
		}
        catch {
            console.log("idk")
        }
	});

    async function register() {
        try{
            // set up POST object
            let body = {}
            body["username"] = username
            body["password"] = password
            body["balance"] = 100
            body["icon_url"] = pib2

            const response = await fetch(`${API_HOST}/auth/register`,{
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem("access_token")}`
                },
                body: JSON.stringify(body)
            })

            if (!response.ok) {
                throw new Error('register failed')
            }

            const data = await response.json();
            user_id = data.balance
            goto(`/login/`)
        } catch(err){
            console.error(err)
        }

    }
    
    async function registerNewToken() {
        try{
            const response = await fetch(`${API_HOST}/auth/register/token`,{
                method: "GET",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem("access_token")}`
                }
            })
            
            if (!response.ok) {
                throw new Error('register failed')
            }
            
            const data = await response.json();
            // user_id = data.balance
            console.log(data)
            token = data.token
            // goto(`/login/`)
        } catch(err){
            console.error(err)
        }

    }

    async function copyText() {
        try {
        await navigator.clipboard.writeText(token ? token : "");
        console.log("Text copied to clipboard!");
        } catch (err) {
        console.error("Failed to copy: ", err);
        }
    }
</script>

<div class="parent-container">
    <div class="parent-subcontainer">
        <div class="title-container">
            <button class="back-btn" on:click={() => goto('/')}>back</button>
            <h1 class="title">Register</h1>
        </div>
        <form on:submit={register} class="login-form">
            <label for="username">Username</label>
            <input 
                id="username"
                bind:value={username}
                type="text"
                required 
                style="max-width: 200px; min-width: 200px;"
            >
            <label for="password">Password</label>
            <input 
                id="password"
                bind:value={password}
                type="password"
                required 
                style="max-width: 200px; min-width: 200px;">
            <button type="submit" style="max-width: 200px; min-width: 200px;">Register</button>
        </form>
            {#if admin}
            <div>
                <h2>Create new register token</h2>
                <button on:click={registerNewToken} style="max-width: 200px; min-width: 200px;">token</button>
            </div>
            {/if}
            {#if token}
            <div>
                <div class="token-div">
                    {token}
                    <!-- <button class="copy-icon" on:click={copyText} title="Copy">📋</button> -->
                </div>
            </div>
            {/if}
        </div>
    </div>

<style>
    .token-div {
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 5px;
        padding: 8px;
    }

    .copy-icon {
        cursor: pointer;
    }
</style>