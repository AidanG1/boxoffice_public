from scrape.numbers_detail import scrape_numbers_detail
from database.db import supabase
import datetime as dt
from colors import bcolors

BACKFILL_DATE = dt.datetime(2025, 8, 1)


def backfill_international_box_office() -> None:
    # get the numbers slug for each movie that has a movie info day on the backfill date
    movie_infos = (
        supabase.table("movie_info_day")
        .select("id, date, movie_id (numbers_slug)")
        .eq("date", BACKFILL_DATE.strftime("%Y-%m-%d"))
        .is_("international_box_office", None)
        .execute()
    )

    print(
        f"{bcolors.OKGREEN}Found {len(movie_infos.data)} movies to backfill international box office for {BACKFILL_DATE.strftime('%Y-%m-%d')}{bcolors.ENDC}"
    )

    # backfill each movie
    for i, movie_info in enumerate(movie_infos.data):
        numbers_slug = movie_info["movie_id"]["numbers_slug"]
        print(
            f"{bcolors.OKCYAN}Index: {i + 1}/{len(movie_infos.data)} - Backfilling international box office for {numbers_slug} on {BACKFILL_DATE.strftime('%Y-%m-%d')}{bcolors.ENDC}"
        )

        # scrape the numbers detail for the movie
        numbers_detail = scrape_numbers_detail(numbers_slug)

        if not numbers_detail:
            print(
                f"{bcolors.FAIL}No numbers detail found for {numbers_slug}{bcolors.ENDC}"
            )
            continue

        # update the movie info day with the international box office
        update_data = {
            "international_box_office": numbers_detail.international_gross
        }

        supabase.table("movie_info_day").update(update_data).eq(
            "id", movie_info["id"]
        ).execute()

        print(
            f"{bcolors.OKGREEN}Backfilled international box office for {numbers_slug} on {BACKFILL_DATE.strftime('%Y-%m-%d')}{bcolors.ENDC}"
        )

    print(
        f"{bcolors.OKGREEN}Backfill complete for international box office on {BACKFILL_DATE.strftime('%Y-%m-%d')}{bcolors.ENDC}"
    )

if __name__ == "__main__":
    backfill_international_box_office()
