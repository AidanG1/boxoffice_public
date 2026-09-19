export type TableType = {
	date: string
	id: string
	is_estimate: boolean
	is_new_release: boolean
	is_preview: boolean
	is_prediction: boolean
	title: string
	movie_id: string
	poster_path: string | null
	revenue: number
	theaters: number | null
	per_theater_revenue: number | null
	yesterday_revenue: number | null
	yesterday_theaters: number | null
	last_week_revenue: number | null
	last_week_theaters: number | null
	theater_change: number | null
	rank: number | null
	days_in_release: number
}
