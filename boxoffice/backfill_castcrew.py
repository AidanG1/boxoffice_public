# go through every movie detail page and add release dates

from scrape.add_castorcrews_to_database import add_castorcrews_to_database
from scrape.convert_credits import convert_credits_to_cast_or_crew
from scrape.tmdb_detail import get_tmdb_details
from database.db import supabase

START_DATE = "2025-01-01"
END_DATE = "2025-07-31"

# go through every cached movie detail page and add release dates
def backfill_castcrew() -> None:
    # get movies released between START_DATE and END_DATE
    all_movies = (
        supabase.table("movie")
        .select("id, title, tmdb_id, castorcrew(*)")
        .gte("release_date", START_DATE)
        .lte("release_date", END_DATE)
        .execute()
    )

    # get new tmdb data for the movie
    for movie in all_movies.data:
        print(f"Processing movie {movie['title']} with castorcrew {len(movie['castorcrew'])}")

        # get the movie details page from tmdb
        details = get_tmdb_details(movie["tmdb_id"])

        if details is None:
            print(f"No details found for movie {movie['tmdb_id']}")
            continue

        # update the castorcrew in the database
        cast_or_crew = convert_credits_to_cast_or_crew(details.credits)

        # check if the length is the same as in the database
        existing_cast_crew = movie["castorcrew"]

        if len(existing_cast_crew) != len(cast_or_crew):
            print(
                f"Removing {len(existing_cast_crew)} existing castorcrew for movie {movie['title']} because the length is different from the new castorcrew length {len(cast_or_crew)}"
            )
            # delete the existing castorcrew and add the new one
            supabase.table("castorcrew").delete().eq("movie_id", movie["id"]).execute()
            add_castorcrews_to_database(cast_or_crew, movie["id"])
        else:
            print(
                f"Castorcrew for movie {movie['title']} is the same length as the new castorcrew, skipping update"
            )

if __name__ == "__main__":
    backfill_castcrew()

