<script lang="ts">
	import { onMount } from 'svelte';
	import { getUserUsersCurrentGet, postIconUsersIconPost } from '../../client';
	import type { IconCreate, PostIconUsersIconPostData, UserRead } from '../../client';
	import { client } from '../../client/client.gen';
	import UserIcon from './UserIcon.svelte';


	let user: UserRead | null = null
	let showSettings: boolean = false
	let icon_url: string | null = null
	let new_icon_url: string | null = null
	// let loading = $state(true);

	onMount(async () => {
		// 1. Pull the token from storage
		const token = localStorage.getItem('access_token');

		// 2. Configure the client with the token if it exists
		client.setConfig({
			headers: {
				// Only add the header if we actually have a token
				...(token && { Authorization: `Bearer ${token}` })
			}
		});
		try {
			const res = await getUserUsersCurrentGet();
			if (res.data) {
				console.log(res.data)
				user = res.data
			}
		} finally {
			console.log("hi")
		}
	});

	const handleIconChange = async (url: string | null = null, random: boolean = false): Promise<UserRead | null> => {
		try {
			if (url || random){
				const data: IconCreate = {icon_url: url ? url : "", random: random}
				const res = await postIconUsersIconPost({body: data})
				return res.data
			}
		} catch {
			console.log("Request error")
			return null
		}

	}

	const updateIcon = async () => {
		const res = await handleIconChange(new_icon_url)
		if (res){
			user = res
		}
		new_icon_url = null
		showSettings = false
	}
	
	const updateRandomIcon = async () => {
		const res = await handleIconChange(null, true)
		if (res){
			user = res
		}
		new_icon_url = null
		showSettings = false
	}

	

	const toggleSettings = () => showSettings = !showSettings
</script>

<div class="settings-container">
	<button on:click={toggleSettings}>
		<UserIcon username={user ? user.username : "Not signed in"} user_icon={user ? user.icon_url : undefined} balance={user ? (user.balance ? user.balance : 0) : 0}/>
	</button>
	<p>{user ? user.username : ""}</p>
	<span class="text-success font-mono">
		${user ? user.balance?.toLocaleString() ?? 0 : 0}
	</span>
	{#if showSettings}
	<div class="settings-float bg-base-200">
		<label style="width: 90%;" for="icon-url">Change Icon</label>
		<input 
			id="icon-url"
			bind:value={new_icon_url}
			type="text"
			style="max-width: 90%; min-width: 90%;"
		>
		<button on:click={updateIcon}>Submit Icon</button>
		<label style="width: 90%;" for="icon-url">Random Icon</label>
		<button on:click={updateRandomIcon}>Generate Icon</button>
	</div>
	{/if}
</div>

<style>
	/* This forces the SVG to actually take up space */
	.settings-container {
		position: relative;
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: space-between;
		padding: 0 12px;
		user-select: none;
		background-color: rgba(255, 255, 255, 0.2);
	}
	.settings-float {
		position: absolute;
		display: flex;
		flex-direction: column;
		align-items: start;
		text-align: left;
		gap: 8px;
		width: 200px;
		height: 300px;
		top: 100%;
		z-index: 10;
		border-radius: 0 5px 5px 5px;
		padding: 12px;
	}
	.settings-container button {
		cursor: pointer;
	}
	.settings-container p {
		user-select: none;
	}
	.icon-container {
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 8px;
		overflow: hidden;
		background-color: oklch(var(--b2)); /* DaisyUI base-200 color */
	}

	.icon-container img {
		width: 100%;
		height: 100%;
		display: block;
		object-fit: cover;
	}

	.placeholder-circle {
		font-weight: bold;
		opacity: 0.5;
	}
</style>
