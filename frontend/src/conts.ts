import { browser } from '$app/environment';

export const API_HOST = browser
	? `${window.location.protocol}//localhost:8051`
	: 'http://localhost:8051'; // Fallback for server-side rendering
