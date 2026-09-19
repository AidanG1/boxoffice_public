import { supabase } from '$lib/supabaseClient.js'
import { error as skerror } from '@sveltejs/kit'

export const load = async ({ params }) => {
    const { category, start_date, end_date } = params

    const { data, error } = await supabase
        .rpc('market_share', {
            category: category,
            start_date: start_date,
            end_date: end_date
        })

    if (error) {
        throw skerror(500, `Error fetching market share data: ${error.message}`)
    }

    if (!data || data.length === 0) {
        throw skerror(404, `No market share data found for category '${category}'`)
    }

    const category_to_display_map = {
        'numbers_genre': 'Numbers Genres',
        'tmdb_genre': 'TMDB Genres',
        'company': 'Production Companies',
        'mpaa': 'MPAA Ratings',
        'language': 'Spoken Languages',
        'country': 'Production Countries',
        'source': 'Source Materials',
        'production_method': 'Production Methods',
        'creative': 'Creative Types',
    }

    const category_to_sum_more_than_one_map = {
        'numbers_genre': false,
        'tmdb_genre': true,
        'company': true,
        'mpaa': false,
        'language': true,
        'country': true,
        'source': false,
        'production_method': false,
        'creative': false
    }

    return {
        market_share: data,
        category,
        category_to_display_map: category_to_display_map,
        sum_more_than_one: category_to_sum_more_than_one_map[category] || false,
        start_date,
        end_date
    }
}