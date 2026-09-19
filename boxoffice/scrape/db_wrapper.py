# It's the same as the cache except doesn't fill the cache at the beginning

import datetime as dt
from urllib import response

import postgrest
from scrape.scrape_types import (
    AddableMovie,
    BoxOfficeDayToInsert,
    SimpleRelease,
)
from database.db import supabase
from supabase import PostgrestAPIResponse
from database.types import (
    Movie,
    Genre,
    Collection,
    ProductionCompany,
    ProductionCountry,
    SpokenLanguage,
    Boxofficeday,
    MovieInfoDay,
    MovieReleaseDate,
)
from typing import Optional, cast
from colors import bcolors


class DBWrapper:
    movie_cache: dict[str, str] = {}
    genre_cache: dict[int, str] = {}
    collection_cache: dict[int, str] = {}
    production_company_cache: dict[int, str] = {}
    production_country_cache: dict[str, str] = {}
    spoken_language_cache: dict[str, str] = {}

    def get_movie_id(self, numbers_slug: str) -> str | None:
        if numbers_slug in self.movie_cache:
            return self.movie_cache[numbers_slug]

        try:
            response = (
                supabase.table("movie")
                .select("id")
                .eq("numbers_slug", numbers_slug)
                .execute()
            )
        except postgrest.exceptions.APIError as e:
            print(f"Error fetching movie ID for {numbers_slug}: {e}")
            return None

        if not response.data:
            return None

        movie_id = response.data[0]["id"]
        self.movie_cache[numbers_slug] = movie_id

        return movie_id

    def get_genre_id(self, tmdb_id: int) -> str | None:
        if tmdb_id in self.genre_cache:
            return self.genre_cache[tmdb_id]

        response = (
            supabase.table("genre")
            .select("id")
            .eq("tmdb_id", tmdb_id)
            .execute()
        )

        if not response.data:
            return None

        genre_id = response.data[0]["id"]
        self.genre_cache[tmdb_id] = genre_id

        return genre_id

    def get_collection_id(self, tmdb_id: int) -> str | None:
        if tmdb_id in self.collection_cache:
            return self.collection_cache[tmdb_id]

        response = (
            supabase.table("collection")
            .select("id")
            .execute()
        )

        if not response.data:
            return None

        collection_id = response.data[0]["id"]
        self.collection_cache[tmdb_id] = collection_id

        return collection_id

    def get_production_company_id(self, tmdb_id: int) -> str | None:
        if tmdb_id in self.production_company_cache:
            return self.production_company_cache[tmdb_id]

        response = (
            supabase.table("production_company")
            .select("id")
            .eq("tmdb_id", tmdb_id)
            .execute()
        )

        if not response.data:
            return None

        production_company_id = response.data[0]["id"]
        self.production_company_cache[tmdb_id] = production_company_id

        return production_company_id

    def get_production_country_id(self, iso_3166_1: str) -> str | None:
        if iso_3166_1 in self.production_country_cache:
            return self.production_country_cache[iso_3166_1]

        response = (
            supabase.table("production_country")
            .select("id")
            .eq("iso_3166_1", iso_3166_1)
            .execute()
        )

        if not response.data:
            return None

        production_country_id = response.data[0]["id"]
        self.production_country_cache[iso_3166_1] = production_country_id

        return production_country_id

    def get_spoken_language_id(self, iso_639_1: str) -> str | None:
        if iso_639_1 in self.spoken_language_cache:
            return self.spoken_language_cache[iso_639_1]

        response = (
            supabase.table("spoken_language")
            .select("id")
            .eq("iso_639_1", iso_639_1)
            .execute()
        )

        if not response.data:
            return None

        spoken_language_id = response.data[0]["id"]
        self.spoken_language_cache[iso_639_1] = spoken_language_id

        return spoken_language_id

    def get_or_create_genre(self, name: str, tmdb_id: int) -> str:
        genre_id = self.get_genre_id(tmdb_id)

        if genre_id is None:
            genre = (
                supabase.table("genre")
                .insert({"name": name, "tmdb_id": tmdb_id})
                .execute()
            )

            first = genre.data[0]

            # add the genre to the cache
            self.genre_cache[tmdb_id] = first["id"]

            return first["id"]

        return genre_id

    def get_or_create_collection(
        self,
        name: str,
        tmdb_id: int,
        poster_path: str | None,
        backdrop_path: str | None,
    ) -> str:
        collection_id = self.get_collection_id(tmdb_id)

        if collection_id is None:
            collection = (
                supabase.table("collection")
                .insert(
                    {
                        "name": name,
                        "tmdb_id": tmdb_id,
                        "poster_path": poster_path,
                        "backdrop_path": backdrop_path,
                    }
                )
                .execute()
            )

            first = collection.data[0]

            # add the collection to the cache
            self.collection_cache[tmdb_id] = first["id"]

            return first["id"]

        return collection_id

    def get_or_create_production_company(
        self, name: str, tmdb_id: int, logo_path: str | None
    ) -> str:
        production_company_id = self.get_production_company_id(tmdb_id)

        if production_company_id is None:
            production_company = (
                supabase.table("production_company")
                .insert({"name": name, "tmdb_id": tmdb_id, "logo_path": logo_path})
                .execute()
            )

            first = production_company.data[0]

            # add the production company to the cache
            self.production_company_cache[tmdb_id] = first["id"]

            return first["id"]

        return production_company_id

    def get_or_create_production_country(self, name: str, iso_3166_1: str) -> str:
        production_country_id = self.get_production_country_id(iso_3166_1)

        if production_country_id is None:
            production_country = (
                supabase.table("production_country")
                .insert({"name": name, "iso_3166_1": iso_3166_1})
                .execute()
            )

            first = production_country.data[0]

            # add the production country to the cache
            self.production_country_cache[iso_3166_1] = first["id"]

            return first["id"]

        return production_country_id

    def get_or_create_spoken_language(self, name: str, iso_639_1: str) -> str:
        spoken_language_id = self.get_spoken_language_id(iso_639_1)

        if spoken_language_id is None:
            print(f"Creating spoken language {name} with iso {iso_639_1}")
            spoken_language = (
                supabase.table("spoken_language")
                .insert({"name": name, "iso_639_1": iso_639_1})
                .execute()
            )

            first = spoken_language.data[0]

            # add the spoken language to the cache
            self.spoken_language_cache[iso_639_1] = first["id"]

            return first["id"]

        return spoken_language_id

    def get_or_create_movie(self, movie_to_add: AddableMovie) -> Movie:
        movie_id = self.get_movie_id(movie_to_add.numbers_slug)

        if movie_id is None:
            movie = (
                supabase.table("movie")
                .insert(
                    {
                        "numbers_slug": movie_to_add.numbers_slug,
                        "numbers_title": movie_to_add.numbers_title,
                        "numbers_synopsis": movie_to_add.numbers_synopsis,
                        "mpaa_rating": movie_to_add.mpaa_rating,
                        "mpaa_rating_date": movie_to_add.mpaa_rating_date,
                        "mpaa_rating_reason": movie_to_add.mpaa_rating_reason,
                        "source": movie_to_add.source,
                        "genre": movie_to_add.genre,
                        "creative_type": movie_to_add.creative_type,
                        "production_method": movie_to_add.production_method,
                        "title": movie_to_add.title,
                        "overview": movie_to_add.overview,
                        "tagline": movie_to_add.tagline,
                        "release_date": movie_to_add.release_date,
                        "runtime": movie_to_add.runtime,
                        "budget": movie_to_add.budget,
                        "homepage": movie_to_add.homepage,
                        "imdb_id": movie_to_add.imdb_id,
                        "original_language": movie_to_add.original_language,
                        "poster_path": movie_to_add.poster_path,
                        "backdrop_path": movie_to_add.backdrop_path,
                        "tmdb_id": movie_to_add.tmdb_id,
                        "wikidata_id": movie_to_add.wikidata_id,
                        "wikipedia_key": movie_to_add.wikipedia_key,
                        "hsx_id": movie_to_add.hsx_id,
                        "hsx_ticker": movie_to_add.hsx_ticker,
                        "collection_id": movie_to_add.collection_id,
                        "keywords": movie_to_add.keywords,
                        "rotten_tomatoes_id": movie_to_add.rotten_tomatoes_id,
                        "fandango_slug": movie_to_add.fandango_slug,
                        "letterboxd_id": movie_to_add.letterboxd_id,
                        "cinemascore": movie_to_add.cinemascore,
                    }
                )
                .execute()
            )

            first = movie.data[0]

            # add the movie to the cache
            self.movie_cache[movie_to_add.numbers_slug] = first["id"]

            return cast(Movie, first)

        return_movie = Movie(
            **movie_to_add.model_dump(),
            id=movie_id,
        )

        return return_movie

    def create_movie_genre(self, movie_id: str, genre_id: str) -> None:
        supabase.table("movie_genre").insert(
            {"movie_id": movie_id, "genre_id": genre_id}
        ).execute()

    def create_movie_production_company(
        self, movie_id: str, production_company_id: str
    ) -> None:
        supabase.table("movie_production_company").insert(
            {"movie_id": movie_id, "production_company_id": production_company_id}
        ).execute()

    def create_movie_production_country(
        self, movie_id: str, production_country_id: str
    ) -> None:
        supabase.table("movie_production_country").insert(
            {"movie_id": movie_id, "production_country_id": production_country_id}
        ).execute()

    def create_movie_spoken_language(
        self, movie_id: str, spoken_language_id: str
    ) -> None:
        supabase.table("movie_spoken_language").insert(
            {"movie_id": movie_id, "spoken_language_id": spoken_language_id}
        ).execute()

    def create_or_update_numbers_daily(
        self,
        movie_id: str,
        date: dt.date,
        revenue: int,
        theaters: int | None,
        is_new_release: bool,
        is_preview: bool,
        is_estimate: bool,
    ) -> bool:
        daily = (
            supabase.table("boxofficeday")
            .select("id")
            .eq("movie_id", movie_id)
            .eq("date", date)
            .execute()
        )

        if daily.data:
            first = daily.data[0]

            supabase.table("boxofficeday").update(
                {
                    "revenue": revenue,
                    "theaters": theaters,
                    "is_new_release": is_new_release,
                    "is_preview": is_preview,
                    "is_estimate": is_estimate,
                }
            ).eq("id", first["id"]).execute()

            print(
                f"{bcolors.OKGREEN}Updated daily numbers for {date} for {movie_id}{bcolors.ENDC}"
            )

            return True
        else:
            supabase.table("boxofficeday").insert(
                {
                    "movie_id": movie_id,
                    "date": date.strftime("%Y-%m-%d"),
                    "revenue": revenue,
                    "theaters": theaters,
                    "is_new_release": is_new_release,
                    "is_preview": is_preview,
                    "is_estimate": is_estimate,
                }
            ).execute()

            print(
                f"{bcolors.OKGREEN}Added daily numbers for {date} for {movie_id}{bcolors.ENDC}"
            )

            return False

    def get_or_create_movie_info(
        self,
        movie_id: str,
        date: dt.date,
        is_backfilled: bool,
        tmdb_popularity: float,
        tmdb_vote_average: float,
        tmdb_vote_count: int,
        imdb_rating: int,
        imdb_votes: int,
        metacritic_rating: Optional[int],
        wikipedia_views: Optional[int],
        hsx_price: Optional[float],
        youtube_sum_1_views: int,
        youtube_sum_3_views: int,
        youtube_sum_all_views: int,
        letterboxd_watched_count: int,
        letterboxd_listed_count: int,
        letterboxd_liked_count: int,
        letterboxd_rating_count: int,
        letterboxd_average_rating: int,
        letterboxd_per_each_rating_counts: list[int],
        rt_popcorn_meter: int,
        rt_tomato_meter: int,
        rt_user_review_count: int,
        international_box_office: int,
    ) -> str:
        # don't create if it already exists
        movie_info = (
            supabase.table("movie_info_day")
            .select("id")
            .eq("movie_id", movie_id)
            .eq("date", date.strftime("%Y-%m-%d"))
            .execute()
        )

        if movie_info.data:
            first = movie_info.data[0]

            return first["id"]

        movie_info = (
            supabase.table("movie_info_day")
            .insert(
                {
                    "movie_id": movie_id,
                    "date": date.strftime("%Y-%m-%d"),
                    "is_backfilled": is_backfilled,
                    "tmdb_popularity": tmdb_popularity,
                    "tmdb_vote_average": tmdb_vote_average,
                    "tmdb_vote_count": tmdb_vote_count,
                    "imdb_rating": imdb_rating,
                    "imdb_votes": imdb_votes,
                    "metacritic_rating": metacritic_rating,
                    "wikipedia_views": wikipedia_views,
                    "hsx_price": hsx_price,
                    "youtube_sum_1_views": youtube_sum_1_views,
                    "youtube_sum_3_views": youtube_sum_3_views,
                    "youtube_sum_all_views": youtube_sum_all_views,
                    "letterboxd_watched_count": letterboxd_watched_count,
                    "letterboxd_listed_count": letterboxd_listed_count,
                    "letterboxd_liked_count": letterboxd_liked_count,
                    "letterboxd_rating_count": letterboxd_rating_count,
                    "letterboxd_average_rating": letterboxd_average_rating,
                    "letterboxd_per_each_rating_counts": letterboxd_per_each_rating_counts,
                    "rt_popcorn_meter": rt_popcorn_meter,
                    "rt_tomato_meter": rt_tomato_meter,
                    "rt_user_review_count": rt_user_review_count,
                    "international_box_office": international_box_office,
                }
            )
            .execute()
        )

        first = movie_info.data[0]

        print(
            f"{bcolors.OKGREEN}Added movie info for {date} for {movie_id}{bcolors.ENDC}"
        )

        return first["id"]

    def get_movie_by_id(self, movie_id: str) -> Movie:
        movie = (
            supabase.table("movie").select("*").eq("id", movie_id).execute()
        )

        return cast(Movie, movie.data[0])

    def bulk_create_box_office_days(
        self, box_office_days_to_create: list[BoxOfficeDayToInsert]
    ) -> None:
        """
        If there is already a box office day for a movie on a date, skips it without saying anything
        """
        unique_dates: set[dt.date] = set()

        for box_office_day in box_office_days_to_create:
            unique_dates.add(box_office_day.date)

        # get the existing box office days for those dates
        existing_box_office_days = (
            supabase.table("boxofficeday")
            .select("date, movie_id")
            .in_("date", [date.strftime("%Y-%m-%d") for date in unique_dates])
            .execute()
        )

        date_movie_id_pairs: set[tuple[dt.date, str]] = set()

        for existing_box_office_day in existing_box_office_days.data:
            date_movie_id_pairs.add(
                (
                    dt.datetime.strptime(
                        existing_box_office_day["date"], "%Y-%m-%d"
                    ).date(),
                    existing_box_office_day["movie_id"],
                )
            )

        # remove the date and movie id pairs from box office days to insert if they already exist
        new_box_office_days_to_create: list[BoxOfficeDayToInsert] = []

        for box_office_day in box_office_days_to_create:
            if (
                box_office_day.date,
                box_office_day.movie_id,
            ) not in date_movie_id_pairs:
                new_box_office_days_to_create.append(box_office_day)

        box_office_dumps = [
            box_office_day.model_dump()
            for box_office_day in new_box_office_days_to_create
        ]

        # check if there are any duplicate movies. If there are, set the second duplicate to have the field double_day to True
        movie_id_to_movie_dump_list: dict[str, list[dict]] = {}

        for box_office_day in box_office_dumps:
            if box_office_day["movie_id"] not in movie_id_to_movie_dump_list:
                movie_id_to_movie_dump_list[box_office_day["movie_id"]] = []

            movie_id_to_movie_dump_list[box_office_day["movie_id"]].append(
                box_office_day
            )

        # if there are any duplicates, set the first double day to True. If there are any 3x or more, throw an error
        for movie_id, movie_dump_list in movie_id_to_movie_dump_list.items():
            if len(movie_dump_list) == 1:
                movie_dump_list[0]["double_day"] = False
                continue
            if len(movie_dump_list) == 2:
                movie_dump_list[0]["double_day"] = True
                movie_dump_list[1]["double_day"] = False
            else:
                raise ValueError(
                    f"There are {len(movie_dump_list)} box office days for {movie_id} on the same day"
                )

        if len(box_office_dumps) == 0:
            print(f"{bcolors.OKCYAN}No new box office days to create{bcolors.ENDC}")
        else:
            # print(box_office_dumps)
            response = supabase.table("boxofficeday").insert(box_office_dumps).execute()

            print(
                f"{bcolors.OKGREEN}Bulk created {len(response.data)} box office days{bcolors.ENDC}"
            )

    def bulk_create_release_dates(
        self, movie_id: str, release_dates: list[SimpleRelease]
    ) -> None:
        # get the existing release dates for the movie
        existing_release_dates = (
            supabase.table("movie_release_date")
            .select("release_date, release_type")
            .eq("movie_id", movie_id)
            .execute()
        )

        existing_release_dates_set: set[tuple[str, str]] = set()

        for existing_release_date in existing_release_dates.data:
            existing_release_dates_set.add(
                (
                    existing_release_date["release_date"],
                    existing_release_date["release_type"],
                )
            )

        # alright we need to change all of the dates
        dates_to_insert: list[dict] = []
        for release in release_dates:
            if release.release_type == "Puerto Rico":
                continue

            date_str = release.date
            date_str = date_str.replace("st,", ",")
            date_str = date_str.replace("nd,", ",")
            date_str = date_str.replace("rd,", ",")
            date_str = date_str.replace("th,", ",")
            date_str = date_str.strip()
            try:
                date_obj = dt.datetime.strptime(date_str, "%B %d, %Y").date()
            except ValueError:
                continue

            release.date = date_obj.strftime("%Y-%m-%d")

            if (release.date, release.release_type) not in existing_release_dates_set:
                dates_to_insert.append(
                    {
                        "movie_id": movie_id,
                        "release_date": release.date,
                        "release_type": release.release_type,
                    }
                )

        if len(dates_to_insert) == 0:
            # print(f"{bcolors.OKCYAN}No new release dates to create{bcolors.ENDC}")
            return

        # convert February 28th, 2025 to date
        response = (
            supabase.table("movie_release_date").insert(dates_to_insert).execute()
        )

        # print the rows created count
        print(
            f"{bcolors.OKGREEN}Bulk created {len(response.data)} release dates{bcolors.ENDC}"
        )


db_wrapper = DBWrapper()
