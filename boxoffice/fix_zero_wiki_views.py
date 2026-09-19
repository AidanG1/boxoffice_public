import datetime as dt
from scrape.movie_info import get_wikipedia_views
from database.db import supabase


START_DATE = dt.datetime(2025, 7, 14)
END_DATE = dt.datetime(2025, 7, 20)

if __name__ == "__main__":
    # find all the movie info days during this period with zero wiki views
    movie_info_days = (
        supabase.table("movie_info_day")
        .select("id, date, movie_id (id, title, wikipedia_key)")
        .gte("date", START_DATE.isoformat())
        .lte("date", END_DATE.isoformat())
        .eq("wikipedia_views", 0)
        .execute()
        .data
    )

    if not movie_info_days:
        print("No movie info days with zero wiki views found.")
    else:
        print(f"Found {len(movie_info_days)} movie info days with zero wiki views.")

    for movie_info_day in movie_info_days:
        wiki_views = get_wikipedia_views(
            movie_info_day["movie_id"]["wikipedia_key"],
            dt.datetime.fromisoformat(movie_info_day["date"]),
        )

        supabase.table("movie_info_day").update(
            {"wikipedia_views": wiki_views}
        ).eq("id", movie_info_day["id"]).execute()

        print(
            f"Updated movie info day {movie_info_day['id']} for movie {movie_info_day['movie_id']['title']} on {movie_info_day['date']} with {wiki_views} views."
        )