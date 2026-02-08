import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: `http://${import.meta.env.VITE_API_URL}:8051/openapi.json`, 
  output: 'src/client',
  plugins: ['@hey-api/client-fetch'], 
});