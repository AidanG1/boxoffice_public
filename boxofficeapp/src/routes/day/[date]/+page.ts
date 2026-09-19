import { supabase } from '$lib/supabaseClient'
import { error as skerror } from '@sveltejs/kit'
import { addDays } from '$lib/utils'
import type { Database, Tables } from '$lib/supabase.types.js'
import type { TableType } from '$lib/components/table_type.js'

const convert_bod_to_table_type = (
	bod: Tables<'boxofficeday'>[],
	date: string,
	release_day_data: Database['public']['Functions']['days_in_release_by_date']['Returns']
): TableType[] => {
	const results: TableType[] = []
	const yesterday = addDays(new Date(date), -1).toISOString().split('T')[0]
	const last_week = addDays(new Date(date), -7).toISOString().split('T')[0]

	for (const row of bod) {
		const row_movie_id = row.movie_id
		// first check if the right date
		if (row.date === date) {
			// find the correct release day data
			let days_in_release = release_day_data.find((rd) => rd.movie_id === row_movie_id.id)?.days_in_release

			if (!days_in_release) {
				days_in_release = 0
			}

			const table_row: TableType = {
				date: row.date,
				id: row.id,
				is_estimate: row.is_estimate,
				is_new_release: row.is_new_release,
				is_preview: row.is_preview,
				is_prediction: false,
				title: row_movie_id.title,
				movie_id: row_movie_id.id,
				poster_path: row_movie_id.poster_path,
				revenue: row.revenue,
				per_theater_revenue: Math.round((100 * row.revenue) / (row.theaters || 1)) / 100,
				theaters: row.theaters,
				yesterday_revenue: null, // will be filled later if exists
				yesterday_theaters: null, // will be filled later if exists
				last_week_revenue: null, // will be filled later if exists
				last_week_theaters: null, // will be filled later if exists
				rank: null, // will be filled later,
				days_in_release: days_in_release
			}
			results.push(table_row)
		} else if (row.date === yesterday) {
			const table_row = results.find((r) => r.date === date && r.movie_id === row_movie_id.id)
			// if the row for yesterday exists, update it
			if (table_row) {
				table_row.yesterday_revenue = row.revenue
				table_row.yesterday_theaters = row.theaters
			}
		} else if (row.date === last_week) {
			const table_row = results.find((r) => r.date === date && r.movie_id === row_movie_id.id)
			if (table_row) {
				table_row.last_week_revenue = row.revenue
				table_row.last_week_theaters = row.theaters
				table_row.theater_change = (table_row.theaters || 0) - (row.theaters || 0)
			}
		}
	}

	// sort results by revenue descending
	results.sort((a, b) => b.revenue - a.revenue)

	// add rank
	results.forEach((row, index) => {
		row.rank = index + 1
	})

	return results
}

const convert_predictions_to_table_type = (
	predictions: Tables<'movie_prediction'>[],
	bod: Tables<'boxofficeday'>[],
	date: string,
	release_day_data: Database['public']['Functions']['days_in_release_by_date']['Returns']
): TableType[] => {
	const results: TableType[] = []

	console.log('converting predictions for date', date, predictions.length)

	for (const row of predictions) {
		const row_movie_id = row.movie_id
		const row_predictions = row.predictions
		const day_difference = (new Date(date) - new Date(row.start_date)) / (1000 * 60 * 60 * 24)

		// console.log('row predictions', row_movie_id.title, 'day difference', day_difference, 'start date', row.start_date, 'date', date)

		if (day_difference < 0) {
			console.log('Skipping future prediction for', row_movie_id.title)
			continue // skip predictions for future dates
		}

		if (day_difference >= row_predictions.length) {
			console.log('Skipping prediction for', row_movie_id.title, 'beyond prediction range')
			continue // skip if we don't have a prediction for that day
		}

		const release_day = release_day_data.find((rd) => rd.movie_id === row_movie_id.id)
		const days_in_release = release_day ? release_day.days_in_release : 0

		const revenue = row_predictions[day_difference] || 0

		const is_new_release = day_difference === 0

		const table_row: TableType = {
			date: date,
			id: row.id,
			is_estimate: false,
			is_new_release: is_new_release,
			is_preview: false,
			is_prediction: true,
			title: row_movie_id.title,
			movie_id: row_movie_id.id,
			poster_path: row_movie_id.poster_path,
			revenue: revenue,
			per_theater_revenue: null, // will be filled later if theaters data is available
			theaters: null, // will be filled later if theaters data is available
			yesterday_revenue: null, // will be filled later if exists
			last_week_revenue: null, // will be filled later if exists
			theater_change: null, // will be filled later if exists
			rank: null, // will be filled later
			days_in_release: days_in_release			
		}

		let yesterday_revenue = null
		let last_week_revenue = null
		let yesterday_theaters = null

		if (day_difference > 1) {
			yesterday_revenue = row_predictions[day_difference - 1] || 1

			if (day_difference > 7) {
				last_week_revenue = row_predictions[day_difference - 7] || 1
			}
		}

		if (last_week_revenue === null) {
			const last_week_bod = bod.find(
				(b) =>
					b.date === addDays(new Date(date), -7).toISOString().split('T')[0] &&
					b.movie_id.id === row_movie_id.id
			)
			if (last_week_bod) {
				last_week_revenue = last_week_bod.revenue
			}

			if (yesterday_revenue === null) {
				const yesterday_bod = bod.find(
					(b) =>
						b.date === addDays(new Date(date), -1).toISOString().split('T')[0] &&
						b.movie_id.id === row_movie_id.id
				)
				if (yesterday_bod) {
					yesterday_revenue = yesterday_bod.revenue
					yesterday_theaters = yesterday_bod.theaters
				}
			}
		}

		table_row.yesterday_revenue = yesterday_revenue
		table_row.last_week_revenue = last_week_revenue
		table_row.yesterday_theaters = yesterday_theaters
		table_row.theater_change = (table_row.theaters || 0) - (yesterday_theaters || 0)

		// console.log(`yesterday revenue for ${row_movie_id.title}:`, yesterday_revenue, 'last week revenue:', last_week_revenue)

		results.push(table_row)
	}

	// sort results by revenue descending
	results.sort((a, b) => b.revenue - a.revenue)

	// add rank
	results.forEach((row, index) => {
		row.rank = index + 1
	})

	console.log('converted predictions', results.length)

	return results
}

export const load = async ({ params }) => {
	console.log('Loading data for date:', params.date)
	const { date } = params

	// verify that date is in YYYY-MM-DD format
	if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
		skerror(400, `Invalid date format ${date}`)
	}

	const prev_day = addDays(new Date(date), -1).toISOString().split('T')[0]
	const last_week = addDays(new Date(date), -7).toISOString().split('T')[0]

	// see if target date is in the future
	const target_date = new Date(date)
	const { data, error } = await supabase
		.from('boxofficeday')
		.select('*, movie_id(poster_path, title, id)')
		.in('date', [date, prev_day, last_week])
		.order('date', { ascending: false })

	if (error) {
		skerror(500, 'Error fetching data')
	}

	if (!data) {
		skerror(404, 'No data found')
	}

	const { data: release_days_data, error: release_days_error } = await supabase.rpc(
		'days_in_release_by_date',
		{ input_date: date }
	)

	if (release_days_error) {
		console.error('Error fetching release days:', release_days_error)
		skerror(500, 'Error fetching release days')
	}

	console.log(`Target date: ${date}, Today: ${new Date().toISOString().split('T')[0]}, Data rows fetched: ${data.length}`)

	if (target_date < new Date()) {
		const converted = convert_bod_to_table_type(data, date, release_days_data)

		return {
			boxoffice: converted,
			date
		}
	}

	const today = new Date()
	const yesterday = new Date()
	yesterday.setDate(today.getDate() - 1)

	const today_str = today.toISOString().split('T')[0]
	const yesterday_str = yesterday.toISOString().split('T')[0]

	// if date is in the future, access predictions
	const { data: predictions, error: predictions_error } = await supabase
		.from('movie_prediction')
		.select('*, movie_id(poster_path, title, id)')
		.in('made_on_date', [today_str, yesterday_str])
		.order('made_on_date', { ascending: false })

	// console.log('predictions for date', today_str, yesterday_str, predictions)

	if (predictions_error) {
		console.error('Error fetching predictions:', predictions_error)
		skerror(500, 'Error fetching predictions')
	}

	const predictions_from_today = predictions.filter((pred) => pred.made_on_date === today_str)
	let relevant_predictions = predictions
	if (predictions_from_today.length > 0) {
		relevant_predictions = predictions_from_today
	}

	// now convert predictions to table type
	const predictions_table = convert_predictions_to_table_type(relevant_predictions, data, date, release_days_data)

	return {
		boxoffice: predictions_table,
		date
	}
}
