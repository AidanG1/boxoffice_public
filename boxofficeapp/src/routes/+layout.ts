export const ssr = import.meta.env.VITE_CLOUDFLARE === 'true'

export const load = ({ url }) => {
	const { pathname } = url

	return {
		pathname
	}
}
