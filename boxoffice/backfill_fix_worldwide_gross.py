from scrape.box_office_mojo_scrape import scrape_box_office_mojo_totals
from database.db import supabase
from colors import  bcolors

FIX_DATE = "2025-08-05"


def backfill() -> None:
    # Get all movie info days from that day
    mids = (
        supabase.table("movie_info_day")
        .select("id, movie_id (id, imdb_id)")
        .eq("date", FIX_DATE)
        .execute()
    )

    for mid in mids.data:
        movie_id = mid["movie_id"]["id"]
        imdb_id = mid["movie_id"]["imdb_id"]

        print(f"{bcolors.OKBLUE}Processing movie {movie_id} ({imdb_id}){bcolors.ENDC}")

        # Scrape the box office mojo totals
        totals = scrape_box_office_mojo_totals(imdb_id)

        if totals:
            print(f"{bcolors.OKGREEN}Updating totals for movie {movie_id}{bcolors.ENDC}")
            update_data = {
                "international_box_office": totals.international_total,
            }
            supabase.table("movie_info_day").update(update_data).eq(
                "id", mid["id"]
            ).execute()
        else:
            print(f"{bcolors.WARNING}No box office mojo totals found for movie {movie_id}{bcolors.ENDC}")

        print(f"{bcolors.OKBLUE}Finished processing movie {movie_id}{bcolors.ENDC}")

    print(f"{bcolors.OKGREEN}Backfill completed for date {FIX_DATE}{bcolors.ENDC}")

if __name__ == "__main__":
    backfill()
