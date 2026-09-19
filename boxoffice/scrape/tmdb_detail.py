# https://api.themoviedb.org/3/movie/607?append_to_response=credits%2Creleases&language=en-US
# https://api.themoviedb.org/3/search/movie?query=Men%20in%20Black&include_adult=false&language=en-US&primary_release_year=1997&page=1

from session import TS
from scrape.scrape_types import AppendedMovieDetails
from requests.exceptions import ConnectionError
from datetime import date


def get_tmdb_id(title: str, year: int, retries: int = 0) -> int:
    if retries > 6: # murder in the woods required 6 retries
        raise ValueError("Too many retries")
    
    title = title.replace("?","")

    url = f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=false&language=en-US&primary_release_year={year}&page=1"
    try:
        r = TS.get(url)
    except ConnectionError:
        print(f"Failed to connect to {url}")
        return get_tmdb_id(title, year, retries + 1)

    data = r.json()

    if "results" not in data:
        print(data)
        raise ValueError("No results key in response")

    results = data["results"]

    if len(results) == 0:
        if (
            retries > 6
        ):  # https://www.themoviedb.org/movie/191820-the-devil-s-violinist this requires 4 retries
            print(f"No results for {title} {year} {url}")
            raise ValueError("No results found")

        if retries % 2 == 0:
            return get_tmdb_id(title, year + retries, retries + 1)
        else:
            return get_tmdb_id(title, year - retries, retries + 1)

    # first result is the best match
    result = results[0]

    if "id" not in result:
        raise ValueError("No id in result")
    
    # result_title = result["title"].lower()

    # if the found title is over 50% longer, retry
    # need to retry if title is too different
    # if abs(len(title) - len(result_title)) > len(title) * 0.5:
    #     print(f"Title length difference too big {title} {result_title} in year {year}")
    #     if retries % 2 == 0:
    #         return get_tmdb_id(title, year + retries, retries + 1)
    #     else:
    #         return get_tmdb_id(title, year - retries, retries + 1)

    # if the first result has no vote average, it's probably not the right movie so retry
    # if ("vote_average" not in result or result["vote_average"] == 0) and year != date.today().year:
    #     print(f"Retrying {title} {year} {url}")
    #     return get_tmdb_id(title, year - retries, retries + 1)

    return result["id"]


def get_tmdb_details(tmdb_id: int) -> AppendedMovieDetails | None:
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?append_to_response=credits%2Creleases%2Cexternal_ids%2Crelease_dates&language=en-US"
    r = TS.get(url)
    data = r.json()

    try:
        return AppendedMovieDetails(**data)
    except Exception as e:
        print(f"Failed to get {url}")
        print(data)
        print(e)
        return None
