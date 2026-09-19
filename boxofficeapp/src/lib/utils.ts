import { supabase } from './supabaseClient'

export const tmdb_path_to_url = (
	path: string,
	size: 'w1280' | 'w500' | 'w185' | 'original' = 'w1280'
) => `https://image.tmdb.org/t/p/${size}${path}`

export const getMovieData = async (movie_id: string) => {
	console.log('Fetching movie data for ID:', movie_id)

	const { data, error } = await supabase
		.from('movie')
		.select(
			'*, movie_production_company(*, production_company(*)), movie_genre(*, genre(*)), movie_production_country(*, production_country(*)), movie_spoken_language(*, spoken_language(*)), castorcrew(*, person(*)), movie_comps:movie_comps_movie_id_fkey(*, comp_id(id, title, release_date, budget)), movie_info_day(*), boxofficeday(*)'
		)
		.eq('id', movie_id)
		.single()

	if (error) {
		throw new Error('Error fetching data: ' + error.message)
	}

	if (!data) {
		throw new Error('No data found')
	}

	if (Array.isArray(data)) {
		throw new Error('Error fetching data')
	}

	const boxofficedays = (data.boxofficeday || []).sort((a, b) => {
		return new Date(a.date).getTime() - new Date(b.date).getTime()
	})

	const movie_info_days = (data.movie_info_day || []).sort((a, b) => {
		return new Date(a.date).getTime() - new Date(b.date).getTime()
	})

	return {
		movie: data,
		boxofficedays: boxofficedays,
		movie_info_days: movie_info_days
	}
}

export type MovieData = typeof getMovieData extends (movie_id: string) => Promise<infer R>
	? R
	: never

export const getMoviePrediction = async (movie_id: string) => {
	console.log('Fetching movie prediction for ID:', movie_id)
	// get predictions
	const { data: predictions, error: predictions_error } = await supabase
		.from('movie_prediction')
		.select('*')
		.eq('movie_id', movie_id)
		.in('made_on_date', [
			new Date().toISOString().split('T')[0],
			new Date(Date.now() - 86400000).toISOString().split('T')[0]
		])
		.order('made_on_date', { ascending: false })

	if (predictions_error) {
		throw new Error('Error fetching predictions')
	}

	if (predictions.length === 2) {
		// if there are two predictions, we assume the first one is from today and the second one is from yesterday
		// remove the yesterday prediction
		predictions.splice(1, 1)
	}

	const prediction = predictions.length > 0 ? predictions[0] : null

	if (!prediction) {
		return null
	}

	return prediction
}

export type PredictionData = typeof getMoviePrediction extends (
	movie_id: string
) => Promise<infer R>
	? R
	: never

export const getScreenerData = async (movie_id: string) => {
	console.log('Fetching screener data for ID:', movie_id)

	const { data: screener_data, error: screener_error } = await supabase
		.from('screener_view')
		.select('*')
		.eq('movie_id', movie_id)
		.single()

	if (screener_error) {
		throw new Error('Error fetching screener data')
	}

	if (!screener_data) {
		throw new Error('No screener data found')
	}
	return screener_data
}

export type ScreenerData = typeof getScreenerData extends (movie_id: string) => Promise<infer R>
	? R
	: never

export const getPercentRanks = async (movie_id: string) => {
	const { data, error } = await supabase.rpc('percent_ranks', {
		input_id: movie_id
	})

	if (error) {
		throw new Error('Error fetching percent ranks: ' + error.message)
	}

	return data
}

export const getMovieWeekends = async (movie_id: string) => {
	const { data, error } = await supabase.rpc('movie_weekends', {
		input_id: movie_id
	})

	if (error) {
		throw new Error('Error fetching percent ranks: ' + error.message)
	}

	return data
}

export const searchMovie = async (query: string) => {
	const { data, error } = await supabase.rpc('search_movies', {
		search_term: query,
		limit_count: 5
	})

	if (error) {
		throw new Error('Error fetching data')
	}

	if (!data || data.length === 0) {
		return []
	}

	return data
}

export type MovieSearchResult = typeof searchMovie extends (query: string) => Promise<(infer R)[]>
	? R
	: never

export const format = (date: Date | string, formatString: string) => {
	if (typeof date === 'string') {
		date = new Date(date)
	}
	const options: Intl.DateTimeFormatOptions = {}
	if (formatString.includes('eee')) options.weekday = 'short'
	if (formatString.includes('MMMM')) options.month = 'long'
	if (formatString.includes('do')) options.day = 'numeric'
	return new Intl.DateTimeFormat('en-US', options).format(date)
}

export const formatKMB = (
	value: number | null,
	fixed: number = 0,
	remove_last_zero: boolean = true
): string => {
	if (value === null || isNaN(value)) {
		return 'N/A'
	}

	if (value < 0) {
		return `-${formatKMB(-value, fixed, remove_last_zero)}`
	}

	let formattedValue = ''
	if (value >= 1e9) {
		formattedValue = `${(value / 1e9).toFixed(fixed)}B`
	} else if (value >= 1e6) {
		formattedValue = `${(value / 1e6).toFixed(fixed)}M`
	} else if (value >= 1e3) {
		formattedValue = `${(value / 1e3).toFixed(fixed)}K`
	} else {
		formattedValue = value.toFixed(fixed)
	}

	if (remove_last_zero && fixed > 0) {
		// Remove trailing zeros and possibly the decimal point if not needed
		formattedValue = formattedValue.replace(/(\.\d*?[1-9])0+([KMB])$/, '$1$2') // e.g. 1.2300M -> 1.23M
		formattedValue = formattedValue.replace(/\.0+([KMB])$/, '$1') // e.g. 1.0M -> 1M
	}
	return formattedValue
}

export const addDays = (date: Date, days: number) => {
	const result = new Date(date)
	result.setUTCDate(result.getUTCDate() + days) // Use UTC methods for consistency
	return result
}

export const dateToYmd = (date: Date) => date.toISOString().split('T')[0]

export const isWithinBoxOfficeNavigationRange = (date: Date) => {
	const targetDate = dateToYmd(date)
	const minDate = '2000-01-01'
	const maxDate = new Date()
	maxDate.setUTCHours(0, 0, 0, 0)
	maxDate.setUTCMonth(maxDate.getUTCMonth() + 1)

	return targetDate >= minDate && targetDate <= dateToYmd(maxDate)
}

export const parseDateString = (dateString: string): Date => {
	return new Date(dateString.replace(/-/g, '/'))
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const deepEqual = (a: any, b: any): boolean => {
	if (a === b) return true
	if (typeof a !== 'object' || typeof b !== 'object' || a == null || b == null) return false

	const keysA = Object.keys(a)
	const keysB = Object.keys(b)

	if (keysA.length !== keysB.length) return false

	for (const key of keysA) {
		if (!keysB.includes(key) || !deepEqual(a[key], b[key])) return false
	}

	return true
}

export const multiSearch = async (query: string) => {
	const { data: movieData, error: movieError } = await supabase
		.from('movie')
		.select('*')
		.ilike('title', `%${query}%`)

	if (movieError) {
		throw new Error('Error fetching movie data')
	}

	const { data: peopleData, error: peopleError } = await supabase
		.from('person')
		.select('*')
		.ilike('name', `%${query}%`)

	if (peopleError) {
		throw new Error('Error fetching people data')
	}

	const { data: companyData, error: companyError } = await supabase
		.from('production_company')
		.select('*')
		.ilike('name', `%${query}%`)

	if (companyError) {
		throw new Error('Error fetching company data')
	}

	return {
		movies: movieData,
		people: peopleData,
		companies: companyData
	}
}

export type MultiSearchResult = typeof multiSearch extends (query: string) => Promise<infer R>
	? R
	: never