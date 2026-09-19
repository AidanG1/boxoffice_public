export const prerender = true

import { getMovieData } from "$lib/utils";

const possible_starting_ids = [
    '5f507808-3a2c-4690-8367-fcb0d86e4bcc', // Paddington 2
    '7e54b434-09d1-4b96-9351-89e0374050bf', // Oppenheimer
]

export const load = async () => {
    const starting_id = possible_starting_ids[Math.floor(Math.random() * possible_starting_ids.length)];

    const movie_data = await getMovieData(starting_id);

    return {
        movie_data
    };
};