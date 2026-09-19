import { supabase } from '$lib/supabaseClient'
import { error as skerror } from '@sveltejs/kit'
import { addDays, parseDateString } from '$lib/utils'
import type { TableType } from '$lib/components/table_type.js'
import type { Database } from '$lib/supabase.types'

type DaySumAverageReturnType = Database['public']['Functions']['day_sum_average']['Returns']

const convert_bod_to_table_type = (
	last_week_data: DaySumAverageReturnType,
	this_week_data: DaySumAverageReturnType,
	date: string,
	release_day_data: Database['public']['Functions']['days_in_release_by_date']['Returns']
): TableType[] => {
	const results: TableType[] = []

	for (const row of this_week_data) {
		const row_movie_id = row.movie_id

		let release_days = release_day_data.find((rd) => rd.movie_id === row_movie_id)
		const days_in_release = release_days ? release_days.days_in_release : 0

		const table_row: TableType = {
			date: date,
			id: '',
			is_estimate: row.is_estimate,
			is_new_release: row.is_new_release,
			is_preview: false,
			is_prediction: false,
			title: row.title,
			movie_id: row.movie_id,
			poster_path: row.poster_path,
			revenue: row.total_revenue,
			per_theater_revenue:
				Math.round((100 * row.total_revenue) / (row.average_theaters || 1)) / 100,
			theaters: Math.round(row.average_theaters),
			yesterday_theaters: null, // will be filled later if exists
			yesterday_revenue: null, // will be filled later if exists
			last_week_revenue: null, // will be filled later if exists
			last_week_theaters: null, // will be filled later if exists
			theater_change: null, // will be filled later if exists
			rank: null, // will be filled later
			days_in_release: days_in_release
		}

		// find yesterday's data
		const last_week_row = last_week_data.find((r) => r.movie_id === row_movie_id)

		if (last_week_row) {
			table_row.last_week_revenue = last_week_row.total_revenue
			table_row.last_week_theaters = Math.round(last_week_row.average_theaters)
			table_row.theater_change =
				Math.round(table_row.theaters || 0) - Math.round(last_week_row.average_theaters)
		}

		results.push(table_row)
	}

	// sort results by revenue descending
	results.sort((a, b) => b.revenue - a.revenue)

	// add rank
	results.forEach((row, index) => {
		row.rank = index + 1
	})

	return results
}

export const load = async ({ params }) => {
	const { friday_date } = params

	// verify that date is in YYYY-MM-DD format
	if (!/^\d{4}-\d{2}-\d{2}$/.test(friday_date)) {
		skerror(400, `Invalid date format ${friday_date}`)
	}

	const target_date = parseDateString(friday_date)
	const target_sunday = addDays(target_date, 2)

	const last_friday = addDays(target_date, -7)
	const last_sunday = addDays(target_sunday, -7)

	// make sure that the date is a Friday
	if (target_date.getDay() !== 5) {
		skerror(400, `Date must be a Friday, got ${friday_date}`)
	}

	// if in future, return 404
	if (target_date > new Date()) {
		return {
			boxoffice: [],
			date: friday_date
		}
	}

	const { data, error } = await supabase.rpc('day_sum_average', {
		start_date: target_date.toISOString().split('T')[0],
		end_date: target_sunday.toISOString().split('T')[0]
	})

	if (error) {
		skerror(500, 'Error fetching data')
	}

	const { data: last_week_data, error: last_week_error } = await supabase.rpc('day_sum_average', {
		start_date: last_friday.toISOString().split('T')[0],
		end_date: last_sunday.toISOString().split('T')[0]
	})

	if (last_week_error) {
		skerror(500, 'Error fetching data')
	}

	if (!data) {
		skerror(404, 'No data found')
	}
	if (!last_week_data) {
		skerror(404, 'No data found for last week')
	}

	const { data: release_days_data, error: release_days_error } = await supabase.rpc(
		'days_in_release_by_date',
		{ input_date: friday_date }
	)

	if (release_days_error) {
		console.error('Error fetching release days:', release_days_error)
		skerror(500, 'Error fetching release days')
	}

	const converted = convert_bod_to_table_type(last_week_data, data, friday_date, release_days_data)

	if (converted.length > 0) {
		return {
			boxoffice: converted,
			date: friday_date
		}
	}
}
