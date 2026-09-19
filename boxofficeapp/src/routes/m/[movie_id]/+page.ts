import { getMovieData, getMoviePrediction, getScreenerData } from '$lib/utils'
import { error as skerror } from '@sveltejs/kit'
import { browser } from '$app/environment'
const SSR_available = import.meta.env.VITE_CLOUDFLARE === 'true'

export const load = async ({ params }) => {
	const { movie_id } = params

	if (!movie_id) {
		throw skerror(400, 'Movie ID is required')
	}

	try {
		const dataPromise = await getMovieData(movie_id)
		const predictionPromise = await getMoviePrediction(movie_id)
		const screenerPromise = await getScreenerData(movie_id)

		console.log('Loading movie data for ID:', movie_id, SSR_available)

		console.log('Data loaded:', {
			data: dataPromise,
			prediction: predictionPromise,
			screener: screenerPromise
		})

		return {
			movie: dataPromise,
			prediction: predictionPromise,
			// prediction: browser ? predictionPromise : await predictionPromise,
			screener: screenerPromise
			// screener: browser ? screenerPromise : await screenerPromise
		}
	} catch (err) {
		console.error('Error loading movie data:', err)
		throw skerror(500, 'Failed to load movie data')
	}
}
