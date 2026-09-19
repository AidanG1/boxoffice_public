// not here, but also need to make pages for different popularity metrics
import { defaultFilters, getBase64Screener, type FilterNameType, type FilterTypeType } from '$lib/screener.js'
import { supabase } from '$lib/supabaseClient'
import { error as skerror } from '@sveltejs/kit'

const allowed_categories = [
	'numbers_genre',
	'tmdb_genre',
	'mpaa',
	'language',
	'country',
	'company',
	'release_year',
	'release_month',
	'release_day',
	'cinemascore',
	'person',
	'person_tmdb_id',
	'character',
	'source',
	'production_method',
	'creative',
	'runtime',
	'budget',
	'keyword'
]

const screenable_categories: Record<string, { name: FilterNameType; type: FilterTypeType }> = {
	budget: {
		name: 'budget',
		type: '='
	},
	mpaa: {
		name: 'mpaa_rating',
		type: '='
	},
	cinemascore: {
		name: 'cinemascore',
		type: '='
	},
	runtime: {
		name: 'runtime',
		type: '='
	},
	company: {
		name: 'production_companies',
		type: 'contains'
	},
	source: {
		name: 'source',
		type: '='
	},
}

const base_function = async (category: string, value: string) => {
	let query
	if (category === 'tmdb_genre') {
		query = supabase
			.from('movie')
			.select('id, movie_genre!inner(genre!inner(name))')
			.ilike('movie_genre.genre.name', value)
	} else if (category === 'mpaa') {
		query = supabase.from('movie').select('id, mpaa_rating').ilike('mpaa_rating', value)
	} else if (category === 'language') {
		query = supabase
			.from('movie')
			.select('id, movie_spoken_language!inner(spoken_language!inner(name))')
			.ilike('movie_spoken_language.spoken_language.name', value)
	} else if (category === 'country') {
		query = supabase
			.from('movie')
			.select('id, movie_production_country!inner(production_country!inner(name))')
			.ilike('movie_production_country.production_country.name', value)
	} else if (category === 'company') {
		query = supabase
			.from('movie')
			.select('id, movie_production_company!inner(production_company!inner(name))')
			.ilike('movie_production_company.production_company.name', value)
	} else if (category === 'release_year') {
		const year = parseInt(value)
		if (isNaN(year) || year < 1888 || year > new Date().getFullYear()) {
			throw new Error(`Invalid year value: ${value}`)
		}
		query = supabase.from('release_date_view').select('id, release_year').eq('release_year', year)
	} else if (category === 'release_month') {
		const month = parseInt(value)
		if (isNaN(month) || month < 1 || month > 12) {
			throw new Error(`Invalid month value: ${value}`)
		}
		query = supabase
			.from('release_date_view')
			.select('id, release_month')
			.eq('release_month', month)
	} else if (category === 'release_day') {
		const day = parseInt(value)
		if (isNaN(day) || day < 1 || day > 31) {
			throw new Error(`Invalid day value: ${value}`)
		}
		query = supabase.from('release_date_view').select('id, release_day').eq('release_day', day)
	} else if (category === 'cinemascore') {
		query = supabase.from('movie').select('id, cinemascore').ilike('cinemascore', value)
	} else if (category === 'person') {
		query = supabase
			.from('movie')
			.select('id, castorcrew!inner(person!inner(name))')
			.ilike('castorcrew.person.name', value)
	} else if (category === 'person_tmdb_id') {
		const intValue = parseInt(value)
		if (isNaN(intValue)) {
			throw new Error(`Invalid TMDB ID value: ${value}`)
		}
		query = supabase
			.from('movie')
			.select('id, castorcrew!inner(person!inner(tmdb_id))')
			.eq('castorcrew.person.tmdb_id', intValue)
	} else if (category === 'character') {
		query = supabase
			.from('movie')
			.select('id, castorcrew!inner(character_name)')
			.ilike('castorcrew.character_name', `%${value}%`)
	} else if (category === 'source') {
		const sourceValue = value.replace('-', '/')
		query = supabase.from('movie').select('id, source').eq('source', sourceValue)
	} else if (category === 'production_method') {
		const methodValue = value.replace('-', '/')
		query = supabase.from('movie').select('id, production_method').eq('production_method', methodValue)
	} else if (category === 'creative') {
		query = supabase.from('movie').select('id, creative_type').eq('creative_type', value)
	} else if (category === 'numbers_genre') {
		query = supabase.from('movie').select('id, genre').eq('genre', value)
	} else if (category === 'runtime') {
		const runtime = parseInt(value)
		if (isNaN(runtime) || runtime < 0) {
			throw new Error(`Invalid runtime value: ${value}`)
		}
		query = supabase.from('movie').select('id, runtime').eq('runtime', runtime)
	} else if (category === 'budget') {
		const budget = parseInt(value)
		if (isNaN(budget) || budget < 0) {
			throw new Error(`Invalid budget value: ${value}`)
		}
		query = supabase.from('movie').select('id, budget').eq('budget', budget)
	} else if (category === 'keyword') {
		query = supabase
			.from('movie')
			.select('id, keywords')
			.contains('keywords', [ value ])
	} else {
		throw new Error(`Unknown category: ${category}`)
	}

	const { data, error } = await query

	console.log(
		`Query for category '${category}' with value '${value}':`,
		query.toString(),
		'Return length:',
		data?.length
	)

	if (error) {
		throw new Error(
			`Error fetching data for category '${category}' with value '${value}': ${error.message}`
		)
	}

	return {
		movies: data.map((movie) => ({
			id: movie.id
		}))
	}
}

export const load = async ({ params }) => {
	const { category, value } = params

	if (!allowed_categories.includes(category)) {
		throw skerror(404, `Category '${category}' not found`)
	}

	if (!value) {
		throw skerror(404, `Value for category '${category}' not found`)
	}

	type BaseFunctionReturn = Awaited<ReturnType<typeof base_function>>

	let result: BaseFunctionReturn

	try {
		result = await base_function(category, value)
	} catch (err) {
		throw skerror(500, `Error fetching movies: ${err.message}`)
	}

	if (!result || !result.movies || result.movies.length === 0) {
		throw skerror(404, `No movies found for category '${category}' with value '${value}'`)
	}

	// now need to convert the result using the ids_to_info rpc function
	const { data: info, error: infoError } = await supabase.rpc('ids_to_info', {
		ids: result.movies.map((m) => m.id)
	})

	if (infoError) {
		throw skerror(500, `Error fetching movie info: ${infoError.message}`)
	}

	let title = ''

	if (category == 'tmdb_genre') {
		title = `Highest grossing movies in TMDB genre '${value}'`
	} else if (category == 'mpaa') {
		title = `Highest grossing movies with MPAA rating '${value}'`
	} else if (category == 'language') {
		title = `Highest grossing movies in language '${value}'`
	} else if (category == 'country') {
		title = `Highest grossing movies from country '${value}'`
	} else if (category == 'company') {
		title = `Highest grossing movies from production company '${value}'`
	} else if (category == 'cinemascore') {
		title = `Highest grossing movies with a Cinemascore of '${value}'`
	} else if (category == 'release_year') {
		title = `Highest grossing movies released in ${value}`
	} else if (category == 'release_month') {
		const monthNames = [
			'January',
			'February',
			'March',
			'April',
			'May',
			'June',
			'July',
			'August',
			'September',
			'October',
			'November',
			'December'
		]
		const monthName = monthNames[parseInt(value) - 1]
		title = `Highest grossing movies released in ${monthName} month`
	} else if (category == 'release_day') {
		title = `Highest grossing movies released on ${value} day`
	} else if (category == 'person') {
		title = `Highest grossing movies featuring ${value}`
	} else if (category == 'person_tmdb_id') {
		title = `Highest grossing movies featuring TMDB ID ${value}`
	} else if (category == 'character') {
		title = `Highest grossing movies featuring character '${value}'`
	} else if (category == 'source') {
		title = `Highest grossing movies from source '${value}'`
	} else if (category == 'production_method') {
		title = `Highest grossing movies with production method '${value}'`
	} else if (category == 'creative') {
		title = `Highest grossing movies with creative type '${value}'`
	} else if (category == 'numbers_genre') {
		title = `Highest grossing movies in Numbers genre '${value}'`
	} else if (category == 'runtime') {
		title = `Highest grossing movies with runtime of ${value} minutes`
	} else if (category == 'budget') {
		title = `Highest grossing movies with budget of $${value}`
	} else if (category == 'keyword') {
		title = `Highest grossing movies with keyword '${value}'`
	} else {
		title = `Highest grossing movies for category '${category}' with value '${value}'`
	}

	let b64: string | null = null

	if (category in screenable_categories) {
		const screenable_category =
			screenable_categories[category as keyof typeof screenable_categories]
		// generate the base64 for the screener
		const screenerBase64 = getBase64Screener([
			...defaultFilters,
			{
				name: screenable_category.name,
				value: value.replace('-', '/'),
				type: screenable_category.type
			}
		])

		b64 = screenerBase64
	}

	return {
		movies: info,
		category,
		value,
		title,
		b64
	}
}
