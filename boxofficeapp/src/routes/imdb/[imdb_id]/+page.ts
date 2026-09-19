import { redirect } from '@sveltejs/kit'
import { supabase } from '$lib/supabaseClient'

export const load = async ({ params }) => {
	const { imdb_id } = params

	if (!imdb_id) {
		throw redirect(302, '/')
	}

	const { data, error } = await supabase
		.from('movie')
		.select('id, imdb_id')
		.eq('imdb_id', imdb_id)

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
