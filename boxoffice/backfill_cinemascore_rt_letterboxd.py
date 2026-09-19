# go through every movie detail page and add release dates

from database.db import supabase
from scrape.cinemascore_search import get_cinemascore
from scrape.rotten_tomatoes_search import get_rotten_tomatoes
from scrape.letterboxd_search import get_letterboxd_id, get_letterboxd_values


# go through every cached movie detail page and add release dates
def backfill() -> None:
    # get all the movie numbers slugs
    all_movies = (
        supabase.table("movie")
        .select("tmdb_id, id, title, release_date")
        .order("release_date")
        .execute()
    )

    i = 2696

    def apply_update(update: dict) -> None:
        print(f"Applying update to the database. Now up until {i + 1}")
        update_without_id = {k: v for k, v in update.items() if k != "id"}
        supabase.table("movie").update(update_without_id).eq(
            "id", update["id"]
        ).execute()

        print(f"Update applied for {update['id']}, index {i}")

    for i, movie in enumerate(all_movies.data[i:], start=i):
        movie_update = {"id": movie["id"]}

        release_year = int(movie["release_date"][:4])
        # Get the cinemascore
        cinemascore = get_cinemascore(movie["title"], release_year)
        if cinemascore:
            print(
                f"Adding Cinemascore of {cinemascore} for {movie['title']} ({release_year})"
            )
            movie_update["cinemascore"] = cinemascore
        else:
            print(f"No Cinemascore found for {movie['title']} ({release_year})")

        # Get the Rotten Tomatoes data
        rt_data = get_rotten_tomatoes(movie["title"], release_year, None)

        if rt_data:
            print(
                f"Adding Rotten Tomatoes data for {movie['title']} ({release_year}) which matched to {rt_data['rotten_tomatoes_title']} ({rt_data['rotten_tomatoes_year']})"
            )
            movie_update["rotten_tomatoes_id"] = rt_data["rotten_tomatoes_slug"]
        else:
            print(f"No Rotten Tomatoes data found for {movie['tmdb_id']}")

        # Get the Letterboxd data
        letterboxd_id = get_letterboxd_id(movie["tmdb_id"])
        if letterboxd_id:
            movie_update["letterboxd_id"] = letterboxd_id
        else:
            print(f"No Letterboxd ID found for {movie['tmdb_id']}")

        apply_update(movie_update)

    print("Backfilled releases")


if __name__ == "__main__":
    backfill()
