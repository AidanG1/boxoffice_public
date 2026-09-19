from colors import bcolors
from database.db import supabase
from database.types import Movie
from scrape.add_castorcrews_to_database import add_castorcrews_to_database
from scrape.cinemascore_search import get_cinemascore
from scrape.convert_credits import convert_credits_to_cast_or_crew
from scrape.rotten_tomatoes_search_fandango import get_rotten_tomatoes
from scrape.tmdb_detail import get_tmdb_details
from scrape.wikipedia_search import wikidata_id_to_wikipedia_id
import datetime as dt
from requests.exceptions import HTTPError


def possible_update_movie(
    movie: Movie,
) -> None:
    movie_release_date = (
        dt.datetime.strptime(movie["release_date"], "%Y-%m-%d")
        if movie["release_date"]
        else None
    )
    cinemascore = movie["cinemascore"]
    print(
        f"Possible Update: Checking for updates to {movie['title']} with release date {movie_release_date} and cinemascore {cinemascore}"
    )
    # possible update should probably just always check tmdb since that's just an API call and very reliable
    tmdb_data = get_tmdb_details(movie["tmdb_id"])

    if tmdb_data is None:
        raise ValueError("No tmdb data found")

    if tmdb_data.release_date is not None:
        movie_release_date = dt.datetime.strptime(tmdb_data.release_date, "%Y-%m-%d")

    if tmdb_data.external_ids.wikidata_id is not None:
        wikipedia_key = wikidata_id_to_wikipedia_id(tmdb_data.external_ids.wikidata_id)
    else:
        wikipedia_key = None

    mpaa_rating: str | None = None

    for release_date in tmdb_data.release_dates.results:
        if release_date.iso_3166_1 == "US":
            for certification in release_date.release_dates:
                if certification.certification != "":
                    mpaa_rating = certification.certification
                    break
            break

    if mpaa_rating is None:
        mpaa_rating = "NR"

    # check for cinemascore
    if (
        (cinemascore is None or cinemascore == "")
        and movie_release_date is not None
        and movie_release_date > dt.datetime.now() - dt.timedelta(days=7)
    ):  # only check for cinemascore if the movie was released in the last 7 days because lots of movies don't have cinemascores and don't want to do needless checks
        cinemascore = get_cinemascore(
            title=movie["title"], year=movie_release_date.year
        )
        print(f"Possible Update: Found cinemascore for {movie['title']}: {cinemascore}")

    fandango_slug = movie["fandango_slug"]
    rotten_tomatoes_id = movie["rotten_tomatoes_id"]
    if fandango_slug is None:
        # if we don't have a fandango slug, try to get it from the rotten tomatoes data
        try:
            rt_data = get_rotten_tomatoes(
               title=movie["title"],
                year=movie_release_date.year if movie_release_date else 2025,
               fandango_slug=None,
            )
        except HTTPError:
            rt_data = None
        if rt_data is not None:
            fandango_slug = rt_data["fandango_slug"]
            rotten_tomatoes_id = rt_data["rotten_tomatoes_slug"]
        else:
            print(
                f"Possible Update: No Rotten Tomatoes data found for {movie['title']}"
            )

    new_movie = {
        "poster_path": tmdb_data.poster_path,
        "budget": tmdb_data.budget,
        "wikidata_id": tmdb_data.external_ids.wikidata_id,
        "wikipedia_key": wikipedia_key,
        "mpaa_rating": mpaa_rating,
        "cinemascore": cinemascore,
        "release_date": tmdb_data.release_date,
        "rotten_tomatoes_id": rotten_tomatoes_id,
        "fandango_slug": fandango_slug,
    }

    # find the differences in the movie and new_movie
    new_data = {}
    for key, value in new_movie.items():
        if movie.get(key) != value:
            new_data[key] = value

    if new_data:
        # update the movie with the new data
        supabase.table("movie").update(new_movie).eq("id", movie["id"]).execute()
        print(
            bcolors.OKCYAN
            + f"Updated movie {movie['numbers_slug']} with new data for {', '.join(new_data.keys())}"
            + bcolors.ENDC
        )

        # ONLY CHANGE THE CAST AND CREW IF THERE ARE OTHER CHANGES

        # also need to possible update cast and crew
        cast_or_crew = convert_credits_to_cast_or_crew(tmdb_data.credits)

        # check if the length is the same as in the database
        existing_cast_crew = (
            supabase.table("castorcrew")
            .select("*")
            .eq("movie_id", movie["id"])
            .execute()
            .data
        )

        if len(existing_cast_crew) != len(cast_or_crew):
            print(
                bcolors.WARNING
                + f"Removing {len(existing_cast_crew)} existing castorcrew for movie {movie['id']} because the length is different from the new castorcrew length {len(cast_or_crew)}"
            )
            # delete the existing castorcrew and add the new one
            supabase.table("castorcrew").delete().eq("movie_id", movie["id"]).execute()
            add_castorcrews_to_database(cast_or_crew, movie["id"])
    else:
        print(
            bcolors.OKGREEN
            + f"No updates needed for {movie['numbers_slug']}"
            + bcolors.ENDC
        )