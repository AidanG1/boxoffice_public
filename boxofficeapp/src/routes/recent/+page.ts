import { supabase } from '$lib/supabaseClient'
import { error as skerror, redirect} from '@sveltejs/kit'

export const load = async () => {
	const { data: first_day, error: first_day_error } = await supabase
		.from('boxofficeday')
		.select('date')
		.order('date', { ascending: false })
		.limit(1)
		.single()

	if (first_day_error) {
		skerror(500, 'Error fetching first date')
	}

    if (!first_day) {
        skerror(404, 'No first date found')
    }

    // redirect to /day/YYYY-MM-DD
    throw redirect(302, `/day/${first_day.date}`)
}
