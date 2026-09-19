# Backfill the database with old movie data
# add the movies, linking tables, accurate daily numbers, and backfilled movie info

import datetime as dt
from colors import bcolors
from supabase import PostgrestAPIResponse

# START_DATE = dt.date(2025, 1, 1)
# END_DATE = dt.date(2025, 2, 6)
START_DATE = dt.date(2026, 4, 4)
END_DATE = dt.date(2026, 4, 11)

"""
Steps:
1. Scrape the daily numbers for the date range without override
2. Add each of the daily numbers to a list of dicts so that they can be bulk added later
3. Add movies to the database one by one
4. Bulk add the daily numbers to the database
5. Start scraping for movie infos, do this in bulk
6. Bulk add the movie infos to the database
"""

from database.types import Movie
from scrape.add_movie_to_database import add_movie_to_database
from scrape.add_daily_to_database import add_daily_to_database
from scrape.numbers_daily import scrape_numbers_daily
from scrape.movie_info import (
    scrape_imdb_stats,
    scrape_tmdb_stats,
    get_wikipedia_views_range,
    get_youtube_trailer_views,
    scrape_box_office_mojo_totals,
    get_rotten_tomatoes,
    get_letterboxd_values,
)
from database.db import supabase


def backfill(start_date: dt.date, end_date: dt.date) -> None:
    for date in range((end_date - start_date).days + 1):
        scrape_date = start_date + dt.timedelta(days=date)

        scraped_daily = scrape_numbers_daily(scrape_date)

        print(
            bcolors.OKGREEN
            + f"Scraped daily numbers for {scrape_date} with {len(scraped_daily)} movies"
            + bcolors.ENDC
        )

        # add the movies
        daily_numbers_to_add = []
        for daily in scraped_daily:
            res = add_movie_to_database(daily.numbers_slug)

            if res is not None:
                daily_numbers_to_add.append(daily)

        add_daily_to_database(daily_numbers_to_add)


def backfill_dated_movie_info(
    backfill_start_date: dt.date, backfill_end_date: dt.date
) -> None:
    if backfill_start_date > backfill_end_date:
        print(
            bcolors.FAIL
            + "The start date is after the end date, please check your inputs"
            + bcolors.ENDC
        )
        return
    # step 1: get box office days for the date range, select the movie join table
    # step 2: get movie info days for the date range
    # step 3: remove the existing movie info days from the list to be scraped
    # step 4: scrape the movie info days
    # step 5: add the movie info days to the database

    # step 1
    box_office_days = (
        supabase.table("boxofficeday")
        .select("movie_id (*), date")
        .gte("date", backfill_start_date)
        .lte("date", backfill_end_date)
        .execute()
    )

    # step 2
    movie_info_days = (
        supabase.table("movie_info_day")
        .select("movie_id", "date")
        .gte("date", backfill_start_date - dt.timedelta(days=10))
        .lte("date", backfill_end_date + dt.timedelta(days=10))
        .execute()
    )

    existing_movie_info_days = [
        (day["movie_id"], day["date"]) for day in movie_info_days.data
    ]

    # step 3
    unique_movies_to_scrape: list[dict] = []
    movie_id_to_start_end_date: dict[str, tuple[dt.date, dt.date]] = {}

    for day in box_office_days.data:
        tup = (day["movie_id"], day["date"])

        date_obj = dt.datetime.strptime(day["date"], "%Y-%m-%d").date()

        if day["movie_id"]["id"] not in movie_id_to_start_end_date:
            movie_id_to_start_end_date[day["movie_id"]["id"]] = (
                date_obj,
                date_obj,
            )
        else:
            prev_start_date, prev_end_date = movie_id_to_start_end_date[
                day["movie_id"]["id"]
            ]
            if date_obj < prev_start_date:
                movie_id_to_start_end_date[day["movie_id"]["id"]] = (
                    date_obj,
                    prev_end_date,
                )
            if date_obj > prev_end_date:
                movie_id_to_start_end_date[day["movie_id"]["id"]] = (
                    prev_start_date,
                    date_obj,
                )

        if tup not in existing_movie_info_days:
            if day["movie_id"] not in unique_movies_to_scrape:
                unique_movies_to_scrape.append(day["movie_id"])
            else:
                pass
                # print(
                #     bcolors.OKCYAN
                #     + f"Skipping {day['movie_id']['id']} on {day['date']} because the movie is already in the list"
                #     + bcolors.ENDC
                # )
        else:
            print(
                bcolors.OKCYAN
                + f"Skipping {day['movie_id']['id']} on {day['date']} because it already exists"
                + bcolors.ENDC
            )

    # need to scrape 10 days before the first box office day
    for movie_id, (start, end) in movie_id_to_start_end_date.items():
        new_start_date = start - dt.timedelta(days=10)
        movie_id_to_start_end_date[movie_id] = (new_start_date, end)

    # step 4
    movie_info_days = []
    for movie in unique_movies_to_scrape:
        movie_start, movie_end = movie_id_to_start_end_date[movie["id"]]
        print(
            bcolors.OKGREEN
            + f"Processing {movie['title']} from {movie_start} to {movie_end}"
            + bcolors.ENDC
        )
        imdb_info = scrape_imdb_stats(movie["imdb_id"])
        yt_info = get_youtube_trailer_views(movie["title"], movie["release_date"][:4])
        tmdb_info = scrape_tmdb_stats(movie["tmdb_id"])
        bom_totals = scrape_box_office_mojo_totals(movie["imdb_id"])
        letterboxd_info = get_letterboxd_values(movie["letterboxd_id"])
        rt_info = get_rotten_tomatoes(
            movie["title"], movie["release_date"][:4], movie["fandango_slug"]
        )

        # get wikipedia views for the range
        # if movie_start < backfill_start_date:
        #     movie_start = backfill_start_date
        if movie_end > backfill_end_date:
            movie_end = backfill_end_date
        if movie["wikipedia_key"] is None:
            wikipedia_views = {}
        else:
            print(movie_start, movie_end)
            wikipedia_views = get_wikipedia_views_range(
                movie["wikipedia_key"], movie_start, movie_end
            )
        if len(wikipedia_views) == 0:
            # generate the wikipedia views but with 0 views
            wikipedia_views = {
                date.strftime("%Y%m%d00"): 0
                for date in [
                    backfill_start_date + dt.timedelta(days=i)
                    for i in range((movie_end - movie_start).days + 1)
                ]
            }

        current_date = movie_start
        for _ in range((movie_end - movie_start).days + 1):
            # find the wikipedia views for the date
            date_value = current_date.strftime("%Y%m%d00")
            if date_value not in wikipedia_views:
                views = 0
            else:
                views = wikipedia_views[date_value]

            # need to convert the date from 2025020500 to 2025-02-05
            date_obj = current_date

            movie_info_days.append(
                {
                    "movie_id": movie["id"],
                    "date": date_obj.strftime("%Y-%m-%d"),
                    "is_backfilled": True,
                    "tmdb_popularity": tmdb_info.tmdb_popularity,
                    "tmdb_vote_average": tmdb_info.tmdb_vote_average,
                    "tmdb_vote_count": tmdb_info.tmdb_vote_count,
                    "imdb_rating": imdb_info.imdb_rating,
                    "imdb_votes": imdb_info.imdb_votes,
                    "metacritic_rating": imdb_info.metacritic_rating,
                    "wikipedia_views": views,
                    "hsx_price": None,
                    "youtube_sum_1_views": yt_info.youtube_sum_1_views,
                    "youtube_sum_3_views": yt_info.youtube_sum_3_views,
                    "youtube_sum_all_views": yt_info.youtube_sum_all_views,
                    "letterboxd_watched_count": (
                        letterboxd_info["watched_count"] if letterboxd_info else 0
                    ),
                    "letterboxd_listed_count": (
                        letterboxd_info["listed_count"] if letterboxd_info else 0
                    ),
                    "letterboxd_liked_count": (
                        letterboxd_info["liked_count"] if letterboxd_info else 0
                    ),
                    "letterboxd_rating_count": (
                        letterboxd_info["rating_count"] if letterboxd_info else 0
                    ),
                    "letterboxd_average_rating": (
                        letterboxd_info["average_rating"] if letterboxd_info else 0
                    ),
                    "letterboxd_per_each_rating_counts": (
                        letterboxd_info["per_each_rating_counts"]
                        if letterboxd_info
                        else [0] * 10
                    ),
                    "rt_popcorn_meter": rt_info["popcorn_meter"] if rt_info else 0,
                    "rt_tomato_meter": rt_info["tomato_meter"] if rt_info else 0,
                    "rt_user_review_count": rt_info["ratingCount"] if rt_info else 0,
                    "international_box_office": (
                        bom_totals.international_total if bom_totals else 0
                    ),
                }
            )
            current_date += dt.timedelta(days=1)

    initial_length = len(movie_info_days)

    # remove the existing movie info days from the list to be added
    movie_info_days = [
        day
        for day in movie_info_days
        if (day["movie_id"], day["date"]) not in existing_movie_info_days
    ]

    print(
        bcolors.OKCYAN
        + f"Scraped {initial_length} movie info days, did not add {initial_length - len(movie_info_days)} existing movie info days"
        + bcolors.ENDC
    )

    if len(movie_info_days) > 0:
        # step 5
        response = supabase.table("movie_info_day").insert(movie_info_days).execute()

        print(
            bcolors.OKGREEN
            + f"Inserted {len(response.data)} movie info days"
            + bcolors.ENDC
        )


def backfill_movie_info() -> None:
    """
    Steps:
    1. Get all the movies
    2. For each movie, establish the amount of time that movie info days should be scraped. These are 30 days before the first box office and every day that it is in theaters, ignoring re-releases
    3. For each movie, run the imdb, yt trailers, and tmdb just once. Run wikipedia views range.
    4. Insert backfilled rows into the database with only the date and wikipedia views changing
    """

    movies: PostgrestAPIResponse[Movie] = supabase.table("movie").select("*").execute()

    for movie in movies.data:
        print(bcolors.OKGREEN + f"Processing {movie['title']}" + bcolors.ENDC)
        # get the first and last boxofficeday
        first_day = (
            supabase.table("boxofficeday")
            .select("*")
            .eq("movie_id", movie["id"])
            .order("date")
            .execute()
        )
        last_day = (
            supabase.table("boxofficeday")
            .select("*")
            .eq("movie_id", movie["id"])
            .order("date", desc=True)
            .execute()
        )

        if len(first_day.data) == 0 or len(last_day.data) == 0:
            continue

        first_day_date = first_day.data[0]["date"]
        last_day_date = last_day.data[0]["date"]

        first_day_date = dt.datetime.strptime(first_day_date, "%Y-%m-%d").date()
        last_day_date = dt.datetime.strptime(last_day_date, "%Y-%m-%d").date()

        # get the wikipedia views for the range
        first_day_date_minus_30 = first_day_date - dt.timedelta(days=30)

        wikipedia_views = get_wikipedia_views_range(
            movie["wikipedia_key"], first_day_date_minus_30, last_day_date
        )

        # get the existing movie info days by date
        existing_movie_info_days: PostgrestAPIResponse[dict] = (
            supabase.table("movie_info_day")
            .select("date")
            .eq("movie_id", movie["id"])
            .execute()
        )

        existing_dates = [day["date"] for day in existing_movie_info_days.data]

        old_keys = list(wikipedia_views.keys())
        # remove the dates that already exist
        for date in old_keys:
            # convert the date from 2025020500 to 2025-02-05
            converted = dt.datetime.strptime(date, "%Y%m%d00").strftime("%Y-%m-%d")
            if converted in existing_dates:
                del wikipedia_views[date]

        # if there are no dates to add, skip the movie
        if len(wikipedia_views) == 0:
            print(
                bcolors.OKCYAN
                + f"Skipping {movie['title']} because there are no dates to add"
                + bcolors.ENDC
            )
            continue

        # get the imdb, yt trailers, and tmdb just once
        imdb_info = scrape_imdb_stats(movie["imdb_id"])

        yt_info = get_youtube_trailer_views(
            movie["title"], int(movie["release_date"][:4])
        )
        tmdb_info = scrape_tmdb_stats(movie["tmdb_id"])

        # insert backfilled rows into the database with only the date and wikipedia views changing
        movie_infos: list[dict] = []

        for date, views in wikipedia_views.items():
            date_obj = dt.datetime.strptime(date, "%Y%m%d00").date()

            movie_infos.append(
                {
                    "movie_id": movie["id"],
                    "date": date_obj.strftime("%Y-%m-%d"),
                    "is_backfilled": True,
                    "tmdb_popularity": tmdb_info.tmdb_popularity,
                    "tmdb_vote_average": tmdb_info.tmdb_vote_average,
                    "tmdb_vote_count": tmdb_info.tmdb_vote_count,
                    "imdb_rating": imdb_info.imdb_rating,
                    "imdb_votes": imdb_info.imdb_votes,
                    "metacritic_rating": imdb_info.metacritic_rating,
                    "wikipedia_views": views,
                    "hsx_price": None,
                    "youtube_sum_1_views": yt_info.youtube_sum_1_views,
                    "youtube_sum_3_views": yt_info.youtube_sum_3_views,
                    "youtube_sum_all_views": yt_info.youtube_sum_all_views,
                }
            )
            print(
                bcolors.OKCYAN
                + f"Adding {movie['title']} on {date_obj} with {views} views"
                + bcolors.ENDC
            )

        response = supabase.table("movie_info_day").insert(movie_infos).execute()

        print(
            bcolors.OKGREEN
            + f"Inserted {movie['title']} with {len(response.data)} movie info days"
            + bcolors.ENDC
        )


if __name__ == "__main__":
    backfill(START_DATE, END_DATE)
    backfill_dated_movie_info(START_DATE, END_DATE)
    # backfill_movie_info()
