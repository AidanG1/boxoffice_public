import { redirect } from '@sveltejs/kit'
import { supabase } from '$lib/supabaseClient'

export const load = async ({ params }) => {
	const { letterboxd_id } = params

	if (!letterboxd_id) {
		throw redirect(302, '/')
	}

	// Assuming getLetterboxdData is a function that fetches data based on letterboxd_id
	const { data, error } = await supabase
		.from('movie')
		.select('id, letterboxd_id')
		.eq('letterboxd_id', letterboxd_id)

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
