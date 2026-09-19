from turtle import rt
from matplotlib.pylab import f
from pydantic import BaseModel, TypeAdapter
import datetime as dt

from datetime import date


class BaseModel(BaseModel):
    # specify the date format here

    def model_dump(self, *args, **kwargs):
        original_dict = super().model_dump(*args, **kwargs)
        for field_name, value in original_dict.items():
            if isinstance(value, date):
                original_dict[field_name] = value.strftime("%Y-%m-%d")
        return original_dict


class ScrapeRelease(BaseModel):
    date: str
    numbers_slug: str
    title: str
    release_type: str


scrape_release_list_adapter = TypeAdapter(list[ScrapeRelease])


class SimpleRelease(BaseModel):
    date: str
    release_type: str


class ScrapeMpaaInfo(BaseModel):
    mpaa_rating: str
    mpaa_rating_reason: str
    mpaa_rating_date: str | None


class ScrapeMovieDetails(BaseModel):
    source: str
    genre: str
    creative_type: str
    production_method: str
    keywords: list[str] | None
    mpaa: ScrapeMpaaInfo
    domestic_releases: list[SimpleRelease]


class ScrapeBoxOfficeTotals(BaseModel):
    domestic_total: int
    international_total: int
    worldwide_total: int


class ScrapeNumbersDetail(BaseModel):
    numbers_slug: str
    numbers_title: str
    release_year: int
    numbers_synopsis: str | None
    mpaa_rating: str
    mpaa_rating_date: str | None
    mpaa_rating_reason: str
    source: str
    genre: str
    creative_type: str
    production_method: str
    keywords: list[str] | None
    domestic_releases: list[SimpleRelease]
    domestic_gross: int
    international_gross: int
    worldwide_gross: int


class ScrapeNumbersDaily(BaseModel):
    numbers_slug: str
    date: dt.date
    revenue: int
    theaters: int | None
    is_preview: bool
    is_new_release: bool
    is_estimate: bool


from typing import List, Optional


class Genre(BaseModel):
    id: int
    name: str


class ProductionCompany(BaseModel):
    id: int
    logo_path: Optional[str]
    name: str
    origin_country: str


class ProductionCountry(BaseModel):
    iso_3166_1: str
    name: str


class SpokenLanguage(BaseModel):
    english_name: str
    iso_639_1: str
    name: str


class Cast(BaseModel):
    adult: bool
    gender: Optional[int]
    id: int
    known_for_department: Optional[str] = None
    name: str
    original_name: str
    popularity: float
    profile_path: Optional[str]
    cast_id: int
    character: str
    credit_id: str
    order: int


class Crew(BaseModel):
    adult: bool
    gender: Optional[int]
    id: int
    known_for_department: Optional[str] = None
    name: str
    original_name: str
    popularity: float
    profile_path: Optional[str]
    credit_id: str
    department: str
    job: str


class Credits(BaseModel):
    cast: List[Cast]
    crew: List[Crew]


class ReleaseCountry(BaseModel):
    certification: str
    descriptors: List[str]
    iso_3166_1: str
    primary: bool
    release_date: str


class Releases(BaseModel):
    countries: List[ReleaseCountry]


class Collection(BaseModel):
    id: int
    name: str
    poster_path: Optional[str]
    backdrop_path: Optional[str]


class MovieDetails(BaseModel):
    adult: bool
    backdrop_path: Optional[str]
    belongs_to_collection: Optional[Collection]
    budget: int
    genres: List[Genre]
    homepage: Optional[str]
    id: int
    imdb_id: str
    origin_country: List[str]
    original_language: str
    original_title: str
    overview: str
    popularity: float
    poster_path: Optional[str]
    production_companies: List[ProductionCompany]
    production_countries: List[ProductionCountry]
    release_date: str
    revenue: int
    runtime: int
    spoken_languages: List[SpokenLanguage]
    status: str
    tagline: Optional[str]
    title: str
    video: bool
    vote_average: float
    vote_count: int


class ExternalIds(BaseModel):
    imdb_id: str
    facebook_id: str | None
    instagram_id: str | None
    twitter_id: str | None
    wikidata_id: str | None


class ReleaseDate(BaseModel):
    certification: str
    descriptors: List[str]
    iso_639_1: str
    release_date: str
    type: int
    note: str


class ReleaseDates(BaseModel):
    iso_3166_1: str
    release_dates: List[ReleaseDate]


class ReleaseDatesList(BaseModel):
    results: List[ReleaseDates]


class AppendedMovieDetails(MovieDetails):
    credits: Credits
    releases: Releases
    external_ids: ExternalIds
    release_dates: ReleaseDatesList


class HSX(BaseModel):
    hsx_id: int | None
    hsx_ticker: str


class PersonToInsert(BaseModel):
    tmdb_id: int
    name: str
    profile_path: Optional[str]


class Credit(BaseModel):
    # credits also need movie id and person id
    is_cast: bool
    character_name: Optional[str]
    credit_order: Optional[int]
    department: Optional[str]
    job: Optional[str]

    person_name: str
    person_tmdb_id: int
    person_profile_path: Optional[str]


class CastOrCrewInsert(BaseModel):
    movie_id: str
    person_id: str
    is_cast: bool
    character_name: Optional[str]
    credit_order: Optional[int]
    department: Optional[str]
    job: Optional[str]


class BoxOfficeDayToInsert(BaseModel):
    movie_id: str
    date: dt.date
    revenue: int
    theaters: int | None
    is_preview: bool
    is_new_release: bool
    is_estimate: bool


class AddableMovie(BaseModel):
    numbers_slug: str
    numbers_title: str
    numbers_synopsis: str | None
    mpaa_rating: str
    mpaa_rating_date: str | None
    mpaa_rating_reason: str
    source: str
    genre: str
    creative_type: str
    production_method: str

    wikipedia_key: Optional[
        str
    ]  # https://www.imdb.com/title/tt2597718/ nothing for this movie
    wikidata_id: Optional[str]

    tmdb_id: int
    backdrop_path: Optional[str]
    budget: int
    homepage: Optional[str]
    imdb_id: str
    original_language: str
    overview: str
    poster_path: Optional[str]
    release_date: str
    runtime: int
    tagline: Optional[str]
    title: str

    hsx_ticker: str | None
    hsx_id: int | None

    keywords: list[str] | None

    collection_id: str | None

    rotten_tomatoes_id: str | None
    fandango_slug: str | None
    letterboxd_id: str | None
    cinemascore: str | None


class MovieToAdd(AddableMovie):
    # these are not ready for direct insertion and some fields need to be renamed
    collection: Optional[Collection]
    castorcrews: list[Credit]
    genres: list[Genre]
    production_companies: list[ProductionCompany]
    production_countries: list[ProductionCountry]
    spoken_languages: list[SpokenLanguage]
    domestic_releases: list[SimpleRelease]


class MovieInfoDay(BaseModel):
    movie_id: str
    date: dt.date
    is_backfilled: bool
    tmdb_popularity: float
    tmdb_vote_average: float
    tmdb_vote_count: int
    imdb_rating: int  # 10 * imdb_rating float
    imdb_votes: int
    metacritic_rating: Optional[int]
    wikipedia_views: Optional[int]
    hsx_price: Optional[float]
    youtube_sum_1_views: int
    youtube_sum_3_views: int
    youtube_sum_all_views: int
    letterboxd_watched_count: int
    letterboxd_listed_count: int
    letterboxd_liked_count: int
    letterboxd_rating_count: int
    letterboxd_average_rating: int
    letterboxd_per_each_rating_counts: List[int]

    rt_popcorn_meter: int
    rt_tomato_meter: int
    rt_user_review_count: int

    international_box_office: int


class TMdBMovieInfo(BaseModel):
    tmdb_popularity: float
    tmdb_vote_average: float
    tmdb_vote_count: int


class IMdBMovieInfo(BaseModel):
    imdb_rating: int
    imdb_votes: int
    metacritic_rating: Optional[int]


class YoutubeMovieInfo(BaseModel):
    youtube_sum_1_views: int
    youtube_sum_3_views: int
    youtube_sum_all_views: int


class LetterboxdMovieInfo(BaseModel):
    letterboxd_watched_count: int
    letterboxd_listed_count: int
    letterboxd_liked_count: int
    letterboxd_rating_average: float
    letterboxd_rating_count: int
