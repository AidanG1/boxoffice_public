# function to add a row to the movies table when a new slug is found

from colors import bcolors
from database.types import Movie
from scrape.add_castorcrews_to_database import add_castorcrews_to_database
from scrape.cinemascore_search import get_cinemascore
from scrape.convert_credits import convert_credits_to_cast_or_crew
from scrape.db_wrapper import db_wrapper
from scrape.hsx_search import search_hsx_ticker
from scrape.letterboxd_search import get_letterboxd_id
from scrape.numbers_detail import scrape_numbers_detail
from scrape.possible_update import possible_update_movie
from scrape.rotten_tomatoes_search_fandango import get_rotten_tomatoes
from scrape.scrape_types import AddableMovie, MovieToAdd
from scrape.tmdb_detail import get_tmdb_id, get_tmdb_details
from scrape.wikipedia_search import wikidata_id_to_wikipedia_id
import postgrest


def add_movie(numbers_slug: str) -> MovieToAdd | None:
    """
    Steps:
    1. Scrape the numbers
    2. Get the wikipedia page
    3. Get the tmdb page
    4. Get the HSX ticker
    """

    numbers_data = scrape_numbers_detail(numbers_slug)

    if numbers_data is None:
        return None

    # print(
    #     bcolors.OKCYAN
    #     + f"Scraped numbers data for {numbers_data.numbers_title} from {numbers_data.release_year}"
    #     + bcolors.ENDC
    # )

    try:
        title = numbers_data.numbers_title
        if title == "Star Wars Ep. VII: The Force Awakens":
            title = "Star Wars: The Force Awakens"
        elif title == "Star Wars Ep. VIII: The Last Jedi":
            title = "Star Wars: The Last Jedi"
        elif title == "Star Wars Ep. IX: The Rise of Skywalker":
            title = "Star Wars: The Rise of Skywalker"
        elif title == "Star Wars Ep. I: The Phantom Menace":
            title = "Star Wars: The Phantom Menace"
        elif title == "Star Wars Ep. II: Attack of the Clones":
            title = "Star Wars: Attack of the Clones"
        elif title == "Star Wars Ep. III: Revenge of the Sith":
            title = "Star Wars: Revenge of the Sith"
        elif title == "Star Wars Ep. IV: A New Hope":
            title = "Star Wars: A New Hope"
        elif title == "Star Wars Ep. V: The Empire Strikes Back":
            title = "Star Wars: The Empire Strikes Back"
        elif title == "Star Wars Ep. VI: Return of the Jedi":
            title = "Star Wars: Return of the Jedi"
        elif title == "Spider-Man: Into The Spider-Verse 3D":
            title = "Spider-Man: Into the Spider-Verse"
        elif title == "Sh*thouse":
            title = "Shithouse"
        elif title == "Âya to majo":
            title = "Earwig and the Witch"
        elif title == "Ironbark":  # for some reason this is true
            title = "The Courier"
        elif title == "Kaijû no kodomo":
            title = "Children of the Sea"
        elif title == "La piscine":
            title = "The Swimming Pool"
        elif title == "F9: The Fast Saga":
            title = "F9"
        elif title == "Un rescate de huevitos":
            title = "An Egg Rescue"
        elif title == "The Youngest Evangelist And The Ministry Of Music":
            title = "The Youngest Evangelist"
        elif title == "American Underdog: The Kurt Warner Story":
            title = "American Underdog"
        elif title == "Laleh Drive":
            title = "Laleh"
        elif title == "Aline, the voice of love":
            title = "Aline"
        elif title == "Eiga Slam Dunk":
            title = "The First Slam Dunk"
        elif (
            title
            == "Demon Slayer: Kimetsu no Yaiba—To the Hashira Training (鬼滅の刃 柱稽古編)"
        ):
            title = "Demon Slayer: Kimetsu no Yaiba -To the Hashira Training"
        elif title == "Salaar: Cease Fire — Part 1":
            title = "Salaar: Part 1 - Ceasefire"
        elif title == "Godzilla Minus One (ゴジラ最新作)":
            title = "Godzilla Minus One"
        elif title == "Sight & Sound Presents: Daniel Live":
            title = "thisneedstofailamatchblablabla"
        # elif title == "Spiral":
        #     title = "Spiral: From the Book of Saw"
        elif title == "Eli Roth Presents: Jimmy and Stiggs":
            title = "Jimmy and Stiggs"
        elif title == "Shin Godjira":
            title = "Shin Godzilla"
        elif title == "AMÉLIE ou la Métaphysique des Tubes":
            title = "Little Amélie or the Character of Rain"
        elif title == "Yek Tasadef Sadeh":
            title = "It Was Just an Accident"

        tmdb_id = get_tmdb_id(title, numbers_data.release_year)
    except ValueError as e:
        print(
            bcolors.FAIL
            + f"Could not get tmdb id for {numbers_data.numbers_title}, skipping"
            + bcolors.ENDC
        )
        return None

    tmdb_data = get_tmdb_details(tmdb_id)

    if tmdb_data is None:
        print(
            bcolors.FAIL
            + f"Could not find tmdb data for {numbers_data.numbers_title}, skipping"
            + bcolors.ENDC
        )
        return None
    else:
        print(
            bcolors.OKCYAN
            + f"Got tmdb data for {numbers_data.numbers_title}"
            + bcolors.ENDC
        )

    wikidata_id = tmdb_data.external_ids.wikidata_id

    if wikidata_id is None:
        print(
            bcolors.FAIL
            + f"Could not find wikidata id for {numbers_data.numbers_title}, skipping"
            + bcolors.ENDC
        )
        english_wikipedia_key = None
    else:
        english_wikipedia_key = wikidata_id_to_wikipedia_id(wikidata_id)

    hsx_data = search_hsx_ticker(numbers_data.numbers_title)

    # print(
    #     bcolors.OKCYAN + f"Got HSX data for {numbers_data.numbers_title}" + bcolors.ENDC
    # )
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

    # need to get the letterboxd id
    try:
        letterboxd_id = get_letterboxd_id(tmdb_data.id)
    except Exception as e:
        print(
            bcolors.FAIL
            + f"Error getting letterboxd id for {numbers_data.numbers_title}: {e}"
            + bcolors.ENDC
        )
        letterboxd_id = None

    if letterboxd_id is None:
        print(
            bcolors.FAIL
            + f"Could not find letterboxd id for {numbers_data.numbers_title}, continuing without it"
            + bcolors.ENDC
        )
    else:
        print(
            bcolors.OKCYAN
            + f"Got letterboxd id for {numbers_data.numbers_title} - {letterboxd_id}"
            + bcolors.ENDC
        )

    rt_data = get_rotten_tomatoes(tmdb_data.title, numbers_data.release_year, None)

    if rt_data is None:
        print(
            bcolors.FAIL
            + f"Could not find Rotten Tomatoes data for {numbers_data.numbers_title}, continuing without it"
            + bcolors.ENDC
        )
        rotten_tomatoes_slug = None
        fandango_slug = None
    else:
        rotten_tomatoes_slug = rt_data["rotten_tomatoes_slug"]
        fandango_slug = rt_data["fandango_slug"]

    # then get cinemascore
    cinemascore = get_cinemascore(tmdb_data.title, numbers_data.release_year)

    if cinemascore is None:
        print(
            bcolors.FAIL
            + f"Could not find Cinemascore for {numbers_data.numbers_title}, continuing without it"
            + bcolors.ENDC
        )
        cinemascore = ""
    else:
        print(
            bcolors.OKCYAN
            + f"Got Cinemascore data for {numbers_data.numbers_title} - {cinemascore}"
            + bcolors.ENDC
        )

    return MovieToAdd(
        numbers_slug=numbers_data.numbers_slug,
        numbers_title=numbers_data.numbers_title,
        numbers_synopsis=numbers_data.numbers_synopsis,
        mpaa_rating=mpaa_rating,
        mpaa_rating_date=numbers_data.mpaa_rating_date,
        mpaa_rating_reason=numbers_data.mpaa_rating_reason,
        source=numbers_data.source,
        genre=numbers_data.genre,
        creative_type=numbers_data.creative_type,
        production_method=numbers_data.production_method,
        wikipedia_key=english_wikipedia_key,
        wikidata_id=wikidata_id,
        tmdb_id=tmdb_data.id,
        backdrop_path=tmdb_data.backdrop_path,
        budget=tmdb_data.budget,
        homepage=tmdb_data.homepage,
        imdb_id=tmdb_data.imdb_id,
        original_language=tmdb_data.original_language,
        overview=tmdb_data.overview,
        poster_path=tmdb_data.poster_path,
        release_date=tmdb_data.release_date,
        runtime=tmdb_data.runtime,
        tagline=tmdb_data.tagline,
        title=tmdb_data.title,
        hsx_ticker=hsx_data.hsx_ticker if hsx_data is not None else None,
        hsx_id=hsx_data.hsx_id if hsx_data is not None else None,
        letterboxd_id=letterboxd_id,
        rotten_tomatoes_id=rotten_tomatoes_slug,
        cinemascore=cinemascore,
        fandango_slug=fandango_slug,
        keywords=numbers_data.keywords,
        collection=tmdb_data.belongs_to_collection,
        castorcrews=convert_credits_to_cast_or_crew(tmdb_data.credits),
        genres=tmdb_data.genres,
        production_companies=tmdb_data.production_companies,
        production_countries=tmdb_data.production_countries,
        spoken_languages=tmdb_data.spoken_languages,
        collection_id=None,
        domestic_releases=numbers_data.domestic_releases,
    )


def add_movie_to_database(numbers_slug: str) -> Movie | None:
    existing_movie_id = db_wrapper.get_movie_id(numbers_slug)
    if existing_movie_id is not None:
        cached_movie = db_wrapper.get_movie_by_id(existing_movie_id)
        if cached_movie is None:
            print(
                bcolors.FAIL
                + f"Could not find movie with id {existing_movie_id}, removing from cache"
                + bcolors.ENDC
            )
            return None
        possible_update_movie(cached_movie)
        return cached_movie

    print(
        bcolors.OKBLUE
        + f"Starting adding movie {numbers_slug} to the database"
        + bcolors.ENDC
    )

    # add the movies and everything necessary to database
    movie = add_movie(numbers_slug)

    if movie is None or movie.imdb_id is None or movie.imdb_id == "":
        # https://www.the-numbers.com/movie/Game-of-Thrones-The-IMAX-Experience#tab=box-office
        # this movie is not on imdb for some annoying reason
        # a movie not being on imdb means shouldn't predict imo
        if movie is None:
            print(
                bcolors.FAIL
                + f"Adding Movie: Could not find movie for {numbers_slug}, skipping"
                + bcolors.ENDC
            )
        else:
            print(
                bcolors.FAIL
                + f"Could not find imdb id for {movie.numbers_title}, skipping"
                + bcolors.ENDC
            )
        return None

    # first step is to get or create the necessary collection, cast or crews, genres, production companies, production countries, and spoken languages

    genre_ids: list[str] = []
    production_company_ids: list[str] = []
    production_country_ids: list[str] = []
    spoken_language_ids: list[str] = []

    collection_id: str | None = None

    # now add the collection, cast or crews, genres, production companies, production countries, and spoken languages to the database
    if movie.collection is not None:
        collection_id = db_wrapper.get_or_create_collection(
            movie.collection.name,
            movie.collection.id,
            movie.collection.poster_path,
            movie.collection.backdrop_path,
        )

    addable_movie = AddableMovie(
        numbers_slug=movie.numbers_slug,
        numbers_title=movie.numbers_title,
        numbers_synopsis=movie.numbers_synopsis,
        mpaa_rating=movie.mpaa_rating,
        mpaa_rating_date=movie.mpaa_rating_date,
        mpaa_rating_reason=movie.mpaa_rating_reason,
        source=movie.source,
        genre=movie.genre,
        production_method=movie.production_method,
        creative_type=movie.creative_type,
        wikipedia_key=movie.wikipedia_key,
        wikidata_id=movie.wikidata_id,
        tmdb_id=movie.tmdb_id,
        backdrop_path=movie.backdrop_path,
        budget=movie.budget,
        homepage=movie.homepage,
        imdb_id=movie.imdb_id,
        original_language=movie.original_language,
        overview=movie.overview,
        poster_path=movie.poster_path,
        release_date=movie.release_date,
        runtime=movie.runtime,
        tagline=movie.tagline,
        title=movie.title,
        hsx_ticker=movie.hsx_ticker,
        hsx_id=movie.hsx_id,
        keywords=movie.keywords,
        collection_id=collection_id,
        rotten_tomatoes_id=movie.rotten_tomatoes_id,
        fandango_slug=movie.fandango_slug,
        letterboxd_id=movie.letterboxd_id,
        cinemascore=movie.cinemascore,
    )

    for genre in movie.genres:
        genre_ids.append(db_wrapper.get_or_create_genre(genre.name, genre.id))

    for production_company in movie.production_companies:
        production_company_ids.append(
            db_wrapper.get_or_create_production_company(
                production_company.name,
                production_company.id,
                production_company.logo_path,
            )
        )

    for production_country in movie.production_countries:
        production_country_ids.append(
            db_wrapper.get_or_create_production_country(
                production_country.name, production_country.iso_3166_1
            )
        )

    for spoken_language in movie.spoken_languages:
        spoken_language_ids.append(
            db_wrapper.get_or_create_spoken_language(
                spoken_language.name, spoken_language.iso_639_1
            )
        )

    print(
        bcolors.OKCYAN
        + f"Added all necessary genres, production companies, production countries, and spoken languages to the database"
        + bcolors.ENDC
    )

    # next step is to add the movie
    try:
        added_movie = db_wrapper.get_or_create_movie(addable_movie)
    except postgrest.exceptions.APIError as e:
        print(
            bcolors.FAIL
            + f"Failed to add movie {movie.numbers_title} to the database: {e}"
            + bcolors.ENDC
        )
        return None
    added_id = added_movie["id"]

    print(
        bcolors.OKGREEN
        + f"Added movie {movie.numbers_title} to the database"
        + bcolors.ENDC
    )

    # then add the people to the database
    add_castorcrews_to_database(movie.castorcrews, added_id)

    # then add the linking rows between the movie and the other tables
    for genre_id in genre_ids:
        db_wrapper.create_movie_genre(added_id, genre_id)

    for production_company_id in production_company_ids:
        db_wrapper.create_movie_production_company(added_id, production_company_id)

    for production_country_id in production_country_ids:
        db_wrapper.create_movie_production_country(added_id, production_country_id)

    for spoken_language_id in spoken_language_ids:
        db_wrapper.create_movie_spoken_language(added_id, spoken_language_id)

    db_wrapper.bulk_create_release_dates(added_id, movie.domestic_releases)

    print(
        bcolors.OKCYAN
        + f"Added movie {movie.numbers_title} linking tables to the database"
        + bcolors.ENDC
    )

    return added_movie
