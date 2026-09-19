import { supabase } from "$lib/supabaseClient"
import type { Database, Tables } from "$lib/supabase.types.js"

// Database['public']['Views']['screener_view']['Row']['name']
export const name_values = [
    'budget',
    'cinemascore',
    'collection_name',
    'creative_type',
    'days_in_theaters',
    'domestic_share',
    'genre',
    'genres',
    'gross_to_budget_ratio',
    'imdb_rating',
    'imdb_vote_count',
    'in_collection',
    'international_box_office',
    'legs',
    'letterboxd_average_rating',
    'letterboxd_liked_count',
    'letterboxd_listed_count',
    'letterboxd_rating_count',
    'letterboxd_watched_count',
    'max_daily_revenue',
    'max_theater_count',
    'max_tmdb_popularity',
    'max_wikipedia_views',
    'metacritic_rating',
    'movie_id',
    'mpaa_rating',
    'opening_day_of_week',
    'opening_day_revenue',
    'opening_weekend_revenue',
    'original_language',
    'preview_ratio',
    'preview_revenue',
    'production_companies',
    'production_countries',
    'production_method',
    'release_date',
    'rt_popcorn_meter',
    'rt_tomato_meter',
    'rt_user_review_count',
    'runtime',
    'source',
    'title',
    'tmdb_vote_average',
    'tmdb_vote_count',
    'domestic_revenue',
    'total_wikipedia_views',
    'worldwide_box_office',
    'youtube_sum_1_views',
    'youtube_sum_3_views',
    'youtube_sum_all_views'
] as const

export const dollar_names = ['budget', 'max_daily_revenue', 'domestic_revenue', 'international_box_office', 'worldwide_box_office', 'opening_weekend_revenue', 'preview_revenue']

export const filter_values = ['contains', '=', '<>', '>', '<', '>=', '<='] as const

export type FilterNameType = (typeof name_values)[number]
export type FilterTypeType = (typeof filter_values)[number]

export interface Filter {
	name: FilterNameType
	value: string | number | string[]
	type: FilterTypeType
}

export interface Sort {
	name: string
	direction: 'asc' | 'desc'
}

export interface ScreenRequest {
	filters: Filter[]
	sort: Sort
}

export const defaultFilters: Filter[] = [
	{
		name: 'release_date',
		value: new Date().toISOString().split('T')[0],
		type: '<'
	},
	{
		name: 'release_date',
		value: '2015-01-01',
		type: '>'
	},
	{
		name: 'domestic_revenue',
		value: '0',
		type: '>'
	}
]

export const defaultSort: Sort = {
	name: 'release_date',
	direction: 'desc'
}

export const getBase64Screener = (filters: Filter[], sort: Sort = defaultSort): string => {
	return btoa(JSON.stringify({ filters, sort }))
}

export const parseBase64Screener = (b64: string): ScreenRequest => {
	try {
		const decoded = atob(b64)
		return JSON.parse(decoded) as ScreenRequest
	} catch (error) {
		console.error('Error parsing base64 screener:', error)
		return { filters: defaultFilters, sort: defaultSort }
	}
}

export const filter_name_to_title = (name: string) => {
	// replace _ with space and capitalize first letters of every word
	return name
		.replaceAll('_', ' ')
		.split(' ')
		.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
		.join(' ')
}

export const screen = async (filters: Filter[] = defaultFilters, sort: Sort = defaultSort) => {
	// implementation goes here
	const query = supabase.from('screener_view').select('*')

	filters.forEach((filter) => {
		if (filter.type === 'contains') {
			query.contains(filter.name, filter.value.split(','))
		} else if (filter.type === '=') {
			query.eq(filter.name, filter.value)
		} else if (filter.type === '<>') {
			query.neq(filter.name, filter.value)
		} else if (filter.type === '>') {
			query.gt(filter.name, filter.value)
		} else if (filter.type === '<') {
			query.lt(filter.name, filter.value)
		} else if (filter.type === '>=') {
			query.gte(filter.name, filter.value)
		} else if (filter.type === '<=') {
			query.lte(filter.name, filter.value)
		}
	})

	// Apply sorting
	query.order(sort.name, { ascending: sort.direction === 'asc' })

	// limit to 50 results
	query.limit(20)

	// Process the screen request
	const { data: screener_view, error } = await query

	if (error) {
		console.error('Error fetching screener data:', error)
		return { screener_view: [], filters, sort, success: false }
	}

	const returnValue = {
		screener_view: screener_view || [],
		filters: filters,
		sort: sort,
		success: true
	}

	// console.log('Screener response:', returnValue)

	return returnValue
}

export type ScreenResult = Awaited<ReturnType<typeof screen>>