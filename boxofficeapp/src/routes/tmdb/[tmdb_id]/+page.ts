import { redirect } from '@sveltejs/kit'
import { supabase } from '$lib/supabaseClient'

export const load = async ({ params }) => {
	const { tmdb_id } = params

	if (!tmdb_id) {
		throw redirect(302, '/')
	}

	// make sure tmdb_id can be converted to an integer
	const tmdbIdInt = parseInt(tmdb_id, 10)
	if (isNaN(tmdbIdInt)) {
		throw redirect(302, '/')
	}

	const { data, error } = await supabase
		.from('movie')
		.select('id, tmdb_id')
		.eq('tmdb_id', tmdbIdInt)

	if (error) {
		console.error('Error fetching movie data:', error)
		throw redirect(302, '/')
	}

	if (data.length === 0) {
		throw redirect(302, '/')
	}

	const movie_id = data[0].id

	// Redirect to the movie page with the movie_id
	throw redirect(302, `/m/${movie_id}`)
}
