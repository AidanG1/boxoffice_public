from optparse import Option
from turtle import title
from typing import Dict, List, Optional, Any, TypedDict
from datetime import datetime

# Define Database type
Database = Dict[str, Any]


class Boxofficeday(TypedDict):
    date: str
    id: str
    is_new_release: bool
    is_preview: bool
    movie_id: str
    revenue: int
    theaters: int | None
    created_at: datetime
    updated_at: datetime


class Castorcrew(TypedDict):
    character_name: Optional[str]
    credit_order: Optional[int]
    department: Optional[str]
    id: str
    is_cast: bool
    job: Optional[str]
    movie_id: str
    person_id: str


class Collection(TypedDict):
    backdrop_path: Optional[str]
    id: str
    name: str
    poster_path: Optional[str]
    tmdb_id: int


class Genre(TypedDict):
    id: str
    name: str
    tmdb_id: int


class Movie(TypedDict):
    backdrop_path: Optional[str]
    budget: Optional[int]
    creative_type: str
    collection_id: Optional[str]
    genre: str
    homepage: Optional[str]
    hsx_id: Optional[int]
    hsx_ticker: Optional[str]
    id: str
    imdb_id: str
    keywords: Optional[List[str]]
    mpaa_rating: str
    mpaa_rating_date: Optional[str]
    mpaa_rating_reason: str
    numbers_slug: str
    numbers_synopsis: Optional[str]
    numbers_title: str
    original_language: str
    overview: str
    poster_path: Optional[str]
    production_method: str
    release_date: str
    runtime: int
    source: str
    tagline: str
    title: str
    tmdb_id: int
    wikipedia_id: Optional[int]
    wikipedia_key: Optional[str]
    wikidata_id: Optional[str]
    letterboxd_id: str
    rotten_tomatoes_id: Optional[str]
    cinemascore: Optional[str]
    fandango_slug: Optional[str]


class MovieGenre(TypedDict):
    genre_id: str
    movie_id: str


class MovieInfoDay(TypedDict):
    date: str
    hsx_price: Optional[float]
    id: str
    imdb_rating: int
    imdb_votes: int
    is_backfilled: bool
    metacritic_rating: Optional[int]
    movie_id: str
    tmdb_popularity: float
    tmdb_vote_average: float
    tmdb_vote_count: int
    wikipedia_views: Optional[int]
    youtube_sum_1_views: Optional[int]
    youtube_sum_3_views: Optional[int]
    youtube_sum_all_views: Optional[int]
    created_at: datetime
    updated_at: datetime
    letterboxd_watched_count: Optional[int]
    letterboxd_listed_count: Optional[int]
    letterboxd_liked_count: Optional[int]
    letterboxd_rating_count: Optional[int]
    letterboxd_average_rating: Optional[int]
    letterboxd_per_each_rating_counts: Optional[list[int]]
    rt_user_liked_score: Optional[int]  # this is the popcorn meter
    rt_critic_liked_score: Optional[int]  # this is the classic tomato meter
    rt_user_average_score: Optional[int]  # it is a float but multiply by 10. This is out of 5
    rt_critic_average_score: Optional[int]  # this is a float but multiply by 10. This is out of 10
    rt_user_review_count: Optional[int]
    rt_user_rating_count: Optional[int]
    rt_want_to_see_count: Optional[int]
    rt_critic_review_count: Optional[int]


class MovieProductionCompany(TypedDict):
    movie_id: str
    production_company_id: str


class MovieProductionCountry(TypedDict):
    movie_id: str
    production_country_id: str


class MovieReleaseDate(TypedDict):
    id: str
    movie_id: str
    release_date: str
    release_type: str


class MovieSpokenLanguage(TypedDict):
    movie_id: str
    spoken_language_id: str


class Person(TypedDict):
    id: str
    name: str
    profile_path: Optional[str]
    tmdb_id: int


class ProductionCompany(TypedDict):
    id: str
    logo_path: Optional[str]
    name: str
    tmdb_id: int


class ProductionCountry(TypedDict):
    id: str
    iso_3166_1: str
    name: str


class SpokenLanguage(TypedDict):
    id: str
    iso_639_1: str
    name: str


class MoviePrediction(TypedDict):
    id: str
    created_at: str
    updated_at: str
    movie_id: str
    predictions: list[int]
    start_date: str
    made_on_date: str



class SumByDayRPC(TypedDict):
    date: str
    revenue: int
    theater_count: int
    budget_sum: int
    theater_weighted_budget: int


class KNNRPC(TypedDict):
    return_id: str
    similarity: float
    title: str
    budget: int

class BulkKNNRPC(KNNRPC):
    similar_id: str

class FirstDaysMultiRPC(TypedDict):
    return_id: str
    date: str
    revenue: int

class OpeningDayDataRPC(TypedDict):
    movie_id: str
    title: str
    opening_date: str
    genre: str
    production_method: str
    budget: int
    opening_day_revenue: int
    in_franchise: bool
    pre_release_cumulative_wikipedia_views: int
    day_before_wikipedia_views: int
    day_before_imdb_rating: int
    day_before_youtube_sum_1_views: int
    day_before_youtube_sum_3_views: int
    day_before_youtube_sum_all_views: int

class PreviewComparisonRPC(TypedDict):
    return_id: str
    title: str
    preview_revenue: int
    first_day_revenue: int
    first_3_days_revenue: int
    first_7_days_revenue: int
    total_revenue: int
