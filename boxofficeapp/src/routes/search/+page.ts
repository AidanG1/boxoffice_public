// read the query parameter of ?q from the URL. That is the search term.
import { searchMovie } from '$lib/utils'
import { redirect } from '@sveltejs/kit'

export async function load({ url }) {
	// if no q parameter, redirect to advanced search page
	if (!url.searchParams.has('q')) {
		throw redirect(302, '/search/advanced')
	}

	const searchTerm = url.searchParams.get('q') || ''
	const results = await searchMovie(searchTerm)

	if (results.length === 0 && searchTerm) {
		// If no results found, redirect to the search page with the query parameter
		throw redirect(302, `/search?q=${encodeURIComponent(searchTerm)}`)
	}

	redirect(302, `/m/${results[0].id}`)
}
