# this is the main code to run every day

"""
# Steps:
## Scraping steps
1. Scrape release schedule https://the-numbers.com/movies/release-schedule for the next month
2. Add new upcoming releases to the database, find wikipedia page, HSX ticker, tmdb page for each
3. Scrape the most recent daily box office
4. Scrape the most recent hsx price
5. Scrape the imdb and metacritic information
6. Scrape YT trailer views

## Modeling steps
7. Rerun the model for every movie implementing all new data
8. Save model results to the database
"""

from command_wrapper import wrap_command
from colors import bcolors
from database.db import supabase
from database.types import Boxofficeday, Movie
from scrape.add_movie_to_database import add_movie_to_database
from scrape.db_wrapper import db_wrapper
from scrape.movie_info import make_movie_info_day
from scrape.numbers_daily import scrape_numbers_daily
from scrape.scrape_releases import scrape_releases
from scrape.scrape_types import SimpleRelease
from today import get_today
from typing import TypedDict
import datetime as dt
import argparse
import multiprocessing


class NotReleasedMovie(TypedDict):
    movie_id: Movie


class NumbersSlug(TypedDict):
    numbers_slug: str


class ExistingMovieInfo(TypedDict):
    movie_id: NumbersSlug


def scrape_movie_infos(today: dt.date, box_office_lookback_days: int = 5) -> None:
    scrape_date = today - dt.timedelta(days=1)
    dates_to_scrape = [
        today - dt.timedelta(days=i) for i in range(box_office_lookback_days)
    ]
    formatted_dates = [dt.date.strftime(date, "%Y-%m-%d") for date in dates_to_scrape]

    existing_box_office_days = (
        supabase.table("boxofficeday")
        .select("date, movie_id (*)")
        .in_("date", formatted_dates)
        .execute()
        .data
    )

    # find existing movie infos from today and don't make those again
    existing_movie_infos = (
        supabase.table("movie_info_day")
        .select("movie_id (numbers_slug)")
        .eq("date", dt.date.strftime(scrape_date, "%Y-%m-%d"))
        .execute()
        .data
    )

    existing_movie_numbers_slugs = set(
        [movie["movie_id"]["numbers_slug"] for movie in existing_movie_infos]
    )

    # Map ids to scrape to movies
    ids_to_movies: dict[str, dict] = {
        daily["movie_id"]["id"]: daily["movie_id"] for daily in existing_box_office_days
    }

    # also need to find movies that aren't out yet based on the movie_release_date table
    for i, movie in enumerate(ids_to_movies.values()):
        # make the movie into a Movie object
        movie_model = Movie(**movie)

        if movie["numbers_slug"] in existing_movie_numbers_slugs:
            print(f"Already have movie info for {movie['numbers_slug']}")
            continue
        mid = make_movie_info_day(movie_model, scrape_date)
        db_wrapper.get_or_create_movie_info(
            mid.movie_id,
            mid.date,
            mid.is_backfilled,
            mid.tmdb_popularity,
            mid.tmdb_vote_average,
            mid.tmdb_vote_count,
            mid.imdb_rating,
            mid.imdb_votes,
            mid.metacritic_rating,
            mid.wikipedia_views,
            mid.hsx_price,
            mid.youtube_sum_1_views,
            mid.youtube_sum_3_views,
            mid.youtube_sum_all_views,
            mid.letterboxd_watched_count,
            mid.letterboxd_listed_count,
            mid.letterboxd_liked_count,
            mid.letterboxd_rating_count,
            mid.letterboxd_average_rating,
            mid.letterboxd_per_each_rating_counts,
            mid.rt_popcorn_meter,
            mid.rt_tomato_meter,
            mid.rt_user_review_count,
            mid.international_box_office,
        )

    # also within the pipeline it is important to scrape the releases before they come out. The goal is to scrape
    not_released_movies = (
        supabase.table("movie_release_date")
        .select("movie_id (*)")
        .gt("release_date", scrape_date)
        .execute()
        .data
    )

    for movie in not_released_movies:
        if movie["movie_id"] is None:
            print(f"Scrape movie infos: Could not find movie for {movie['movie_id']}")
            continue

        # if it is already in the database, skip it
        if movie["movie_id"]["numbers_slug"] in existing_movie_numbers_slugs:
            print(f"Already have movie info for {movie['movie_id']['numbers_slug']}")
            continue

        mid = make_movie_info_day(movie["movie_id"], scrape_date)
        db_wrapper.get_or_create_movie_info(
            mid.movie_id,
            mid.date,
            mid.is_backfilled,
            mid.tmdb_popularity,
            mid.tmdb_vote_average,
            mid.tmdb_vote_count,
            mid.imdb_rating,
            mid.imdb_votes,
            mid.metacritic_rating,
            mid.wikipedia_views,
            mid.hsx_price,
            mid.youtube_sum_1_views,
            mid.youtube_sum_3_views,
            mid.youtube_sum_all_views,
            mid.letterboxd_watched_count,
            mid.letterboxd_listed_count,
            mid.letterboxd_liked_count,
            mid.letterboxd_rating_count,
            mid.letterboxd_average_rating,
            mid.letterboxd_per_each_rating_counts,
            mid.rt_popcorn_meter,
            mid.rt_tomato_meter,
            mid.rt_user_review_count,
            mid.international_box_office,
        )


def add_releases() -> None:
    # scrape releases but only for the future, no date in  these
    releases = scrape_releases(until_days=10)

    # want to add releases in the case that they are wide releases
    releases = [r for r in releases if "Wide" in r.release_type]

    for release in releases:
        movie = add_movie_to_database(release.numbers_slug)

        if movie is None:
            print(f"Add releases: Could not find movie for {release.numbers_slug}")
            continue

        db_wrapper.bulk_create_release_dates(
            movie["id"],
            [
                SimpleRelease(**{"date": r.date, "release_type": r.release_type})
                for r in releases
            ],
        )


def scrape_today(
    today: dt.date,
) -> None:
    try:
        scraped_daily = scrape_numbers_daily(today, override_html=True)
    except ValueError as e:
        print(
            bcolors.WARNING
            + f"Daily chart for {today} unavailable; skipping current-day scrape ({e})"
            + bcolors.ENDC
        )
        return

    movies = [add_movie_to_database(daily.numbers_slug) for daily in scraped_daily]

    for i, daily in enumerate(scraped_daily):
        movie = movies[i]
        if movie is None:
            print(f"Scrape today: could not find movie for {daily.numbers_slug}")
            continue
        db_wrapper.create_or_update_numbers_daily(
            movie["id"],
            daily.date,
            daily.revenue,
            daily.theaters,
            daily.is_new_release,
            daily.is_preview,
            daily.is_estimate,
        )


def rescrape_old_days(
    today: dt.date,
    days_to_repeat: int = 3,
) -> None:
    dates = [today - dt.timedelta(days=i + 1) for i in range(days_to_repeat)]

    # for each of the dates, reget the numbers daily
    for date in dates:
        scraped_daily = scrape_numbers_daily(date, override_html=True)

        update_count = 0

        # update everything
        for daily in scraped_daily:
            # need to get the movie id from db wrapper
            movie_id = db_wrapper.get_movie_id(daily.numbers_slug)

            if movie_id is None:
                print(
                    f"Rescrape old days: Could not find movie id for {daily.numbers_slug}"
                )
                continue

            updated = db_wrapper.create_or_update_numbers_daily(
                movie_id,
                daily.date,
                daily.revenue,
                daily.theaters,
                daily.is_new_release,
                daily.is_preview,
                daily.is_estimate,
            )

            if updated:
                update_count += 1

        print(f"Updated {date} with {update_count} estimates")


def full_pipeline() -> None:
    parser = argparse.ArgumentParser(description="Run the box office pipeline")
    # check if we want to run the pipeline in daily or hourly mode
    parser.add_argument(
        "--daily",
        action="store_true",
        help="Run the pipeline in daily mode, which will scrape the last 92 days",
    )
    parser.add_argument(
        "--hourly",
        action="store_true",
        help="Run the pipeline in hourly mode, which will scrape the last 30 days",
    )
    args = parser.parse_args()
    if not args.daily and not args.hourly:
        print("Please specify either --daily or --hourly")
        exit(1)

    today = get_today()

    print(
        bcolors.BOLD
        + f"Running pipeline for {today} in {'daily' if args.daily else 'hourly'} mode"
        + bcolors.ENDC
    )

    if args.daily:
        # Once per day, scrape the releases and add movie infos for the releases
        # Additionally, add movie infos for all movies that reported in the last 5 days
        add_releases()
        scrape_movie_infos(today, box_office_lookback_days=5)

    if args.hourly:
        # Once per hour, scrape the daily box office. Also re-scrape the past 5 days
        scrape_today(today)
        rescrape_old_days(
            today,
            days_to_repeat=4,
        )

    # now refresh the screener view by calling the rpc function
    # Run the refresh in the background using multiprocessing
    
    def refresh_screener():
        supabase.rpc("refresh_screener_view").execute()
    
    process = multiprocessing.Process(target=refresh_screener)
    process.start()

    print(bcolors.OKGREEN + "Screener view refreshed" + bcolors.ENDC)

    print(bcolors.BOLD + "Pipeline completed successfully!" + bcolors.ENDC)


if __name__ == "__main__":
    wrap_command(full_pipeline)
