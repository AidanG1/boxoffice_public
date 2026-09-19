// Tauri doesn't have a Node.js server to do proper SSR
// so we will use adapter-static to prerender the app (SSG)
// See: https://v2.tauri.app/start/frontend/sveltekit/ for more info
import adapterStatic from '@sveltejs/adapter-static'
import adapterCloudflare from '@sveltejs/adapter-cloudflare'
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'

import dotenv from 'dotenv'

dotenv.config()

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		adapter: process.env.CLOUDFLARE
			? adapterCloudflare()
			: adapterStatic({
					fallback: 'index.html'
				})
	}
}

export default config
