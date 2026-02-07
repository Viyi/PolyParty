<script>
	import { goto } from '$app/navigation';
	import '../../app.css';
	import { client } from '../../client/client.gen';
	import { API_HOST } from '../../conts';

	let username = '';
	let password = '';

	async function login(event) {
		// Prevent the default browser form submission (page reload)
		if (event) event.preventDefault();

		try {
			const formData = new URLSearchParams();
			formData.append('username', username);
			formData.append('password', password);

			const response = await fetch(`${API_HOST}/auth/login`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded'
				},
				body: formData.toString()
			});

			if (!response.ok) throw new Error('login failed');

			const data = await response.json();

			localStorage.setItem('access_token', data.access_token);
			localStorage.setItem('user_id', data.user_id);

			client.setConfig({
				baseUrl: API_HOST,
				headers: {
					Authorization: `Bearer ${data.access_token}`
				}
			});
			goto('/home/');
		} catch (err) {
			console.error(err);
		}
	}
</script>

<div class="parent-container">
	<div class="parent-subcontainer">
		<div class="title-container">
			<button class="back-btn" type="button" on:click={() => goto('/')}>back</button>
			<h1 class="title">Login</h1>
		</div>

		<form on:submit={login} class="login-form">
			<label for="username">Username</label>
			<input
				id="username"
				bind:value={username}
				type="text"
				required
				style="max-width: 200px; min-width: 200px;"
			/>

			<label for="password">Password</label>
			<input
				id="password"
				bind:value={password}
				type="password"
				required
				style="max-width: 200px; min-width: 200px;"
			/>

			<button type="submit" style="max-width: 200px; min-width: 200px; margin-top: 1rem;">
				Login
			</button>
		</form>
	</div>
</div>

<style>
	.login-form {
		display: flex;
		flex-direction: column;
	}
</style>
