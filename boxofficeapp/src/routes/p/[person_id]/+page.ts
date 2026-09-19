import { error as skerror } from '@sveltejs/kit'
import { supabase } from '$lib/supabaseClient'

export const load = async ({ params }) => {
	const { person_id } = params

	if (!person_id) {
		throw skerror(400, 'Person ID is required')
	}

	const { data, error } = await supabase
		.from('person')
		.select(`*, castorcrew (*, movie (id, title, poster_path, release_date))`)
		.eq('id', person_id)
		.single()

	if (error) {
		console.error('Error loading person data:', error)
		throw skerror(500, 'Failed to load person data')
	}

	if (!data) {
		console.error('No person data found')
		throw skerror(404, 'Person not found')
	}

	return { person: data }
}
