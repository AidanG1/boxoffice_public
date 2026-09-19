# add a movie info day for August 1st for each movie that doesn't have one. Scrape all of the information into it.

from database.db import supabase
import datetime as dt
from scrape.db_wrapper import db_wrapper
from scrape.movie_info import make_movie_info_day
from database.types import Movie

ADD_DATE = dt.datetime(2025, 8, 1)


def backfill_movie_info_rt_letterboxd() -> None:
    # get all the movies
    all_movies = (
        supabase.table("movie").select("*").order("release_date", desc=True).execute()
    )

    # movies with movie info days on August 1st
    movies_with_aug_1 = (
        supabase.table("movie_info_day")
        .select("movie_id")
        .eq("date", ADD_DATE)
        .execute()
    )

    # create a set of movie IDs that already have an info day on August 1st
    existing_movie_ids = {movie["movie_id"] for movie in movies_with_aug_1.data}

    # filter movies that do not have an info day on August 1st
    movies_to_backfill = [
        movie for movie in all_movies.data if movie["id"] not in existing_movie_ids
    ]

    print(
        f"Found {len(movies_to_backfill)} movies to backfill for {ADD_DATE.strftime('%Y-%m-%d')}"
    )

    # backfill each movie
    for i, movie in enumerate(movies_to_backfill):
        # make the movie into a Movie object
        print(f"Index: {i + 1}/{len(movies_to_backfill)} - Backfilling movie info for {movie['numbers_slug']} on {ADD_DATE.strftime('%Y-%m-%d')}")
        movie_model = Movie(**movie)
        mid = make_movie_info_day(movie_model, ADD_DATE)
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

        print(
            f"Index: {i}/{len(movies_to_backfill)} - Backfilled movie info for {movie['numbers_slug']} on {ADD_DATE.strftime('%Y-%m-%d')}. Is backfilled: {mid.is_backfilled}. Letterboxd average rating: {mid.letterboxd_average_rating}, RT tomato meter: {mid.rt_tomato_meter}, Wikipedia views: {mid.wikipedia_views}, TMDB Vote Average: {mid.tmdb_vote_average}, IMDB Rating: {mid.imdb_rating}, Metacritic Rating: {mid.metacritic_rating}, YT views: {mid.youtube_sum_all_views}"
        )

if __name__ == "__main__":
    backfill_movie_info_rt_letterboxd()
