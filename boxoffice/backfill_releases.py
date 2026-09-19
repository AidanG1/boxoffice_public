# go through every movie detail page and add release dates

from scrape.db_wrapper import db_wrapper
from scrape.numbers_detail import scrape_numbers_detail
from database.db import supabase

# go through every cached movie detail page and add release dates
def backfill_releases() -> None:
    # get all the movie numbers slugs
    all_movies = supabase.table("movie").select("numbers_slug, id").execute()

    for movie in all_movies.data:
        # get the movie details page
        details = scrape_numbers_detail(movie["numbers_slug"])

        # if there are no domestic releases, skip
        if not details.domestic_releases:
            continue

        print(f"Adding releases for {movie['numbers_slug']}, {details.domestic_releases}")

        # add the domestic releases to the database
        db_wrapper.bulk_create_release_dates(
            movie["id"],
            details.domestic_releases,
        )

    print("Backfilled releases")

if __name__ == "__main__":
    backfill_releases()

