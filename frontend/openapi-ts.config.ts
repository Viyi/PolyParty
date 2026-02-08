import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
	input: `http://10.0.0.165:8051/openapi.json`,
	output: 'src/client',
	plugins: ['@hey-api/client-fetch']
});
