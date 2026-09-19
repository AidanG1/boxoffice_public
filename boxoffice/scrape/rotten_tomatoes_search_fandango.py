# https://www.fandango.com/napi/home/autocompleteDesktopSearch?search=superman
# https://www.fandango.com/napi/fanAndCriticReviews/230934/:pageSize

from platform import release
from typing import TypedDict, Any
from session import S

headers = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://www.fandango.com/superman-2025-230934/movie-overview",
    "X-Requested-With": "XMLHttpRequest",
    "DNT": "1",
    "Sec-GPC": "1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Connection": "keep-alive",
}


class FandangoMovie(TypedDict):
    id: str
    name: str
    link: str
    releaseDate: str
    poster: dict[str, Any]


class FandangoResultMovieWrapper(TypedDict):
    type: str
    items: list[FandangoMovie]


class FandangoResultTypeWrapper(TypedDict):
    type: str  # The result type, e.g., "movies", "theaters", etc.
    items: list[Any]


class FandangoResultsByType(TypedDict):
    locations: FandangoResultTypeWrapper
    movies: FandangoResultMovieWrapper
    theaters: FandangoResultTypeWrapper
    trailers: FandangoResultTypeWrapper


class FandangoResult(TypedDict):
    isEmpty: bool
    seeMoreLink: str
    resultsByType: FandangoResultsByType


class FandangoSearchFound(TypedDict):
    name: str
    releaseDate: str
    link_id: str
    fandango_slug: str


class RottenTomatoesResult(TypedDict):
    rotten_tomatoes_slug: str
    fandango_slug: str

    popcorn_meter: int  # this is the classic popcorn meter
    ratingCount: int
    tomato_meter: int  # this is the classic tomato meter


def fandango_search(
    title: str, year: int, fandango_slug: str | None
) -> FandangoSearchFound | None:
    url = f"https://www.fandango.com/napi/home/autocompleteDesktopSearch?search={title}"

    r = S.get(url, headers=headers)

    r.raise_for_status()

    data: FandangoResult = r.json()

    if data is None:
        print(f"Fandango is None for {title} ({year}) ")
        return None

    if data["isEmpty"]:
        print(f"Fandango result is empty for {title} ({year})")
        return None

    for movie in data["resultsByType"]["movies"]["items"]:

        if "releaseDate" not in movie:
            print(f"{movie['name']} has no release date")
            # assume it is correct
            release_year = str(year)
        else:
            release_year = movie["releaseDate"][:4]
        print(f"Fandango checking movie: {movie['name']} ({release_year})")
        proposed_slug = movie["link"].split("/")[1]

        if (
            fandango_slug is None
            and title.lower() in movie["name"].lower()
            and str(year) == release_year
        ) or (fandango_slug is not None and proposed_slug == fandango_slug):
            # link looks like /superman-2025-230934/movie-overview
            # we want the last part, which is the movie ID
            movie_id = movie["link"].split("/")[1].split("-")[-1]
            return FandangoSearchFound(
                name=movie["name"],
                releaseDate=movie["releaseDate"] if "releaseDate" in movie else "",
                link_id=movie_id,
                fandango_slug=proposed_slug,
            )

    print(f"No Fandango matching results found for {title} ({year})")

    return None


class FandangoReviewsData(TypedDict):
    audienceRating: str
    audienceScore: str  # 93%
    certifiedFresh: bool
    criticsRating: str
    criticsReviews: list[Any]
    criticsScore: str  # 83%
    isReviewable: bool
    isVerifiable: bool
    ratingCount: int
    reviewableOn: str
    reviews: list[Any]
    rottenTomatoesUrl: str  # https://www.rottentomatoes.com/m/superman_2025


class FandangoReviewsResponse(TypedDict):
    movieId: str
    error: Any
    data: FandangoReviewsData


def get_rotten_tomatoes(
    title: str, year: int, fandango_slug: str | None
) -> RottenTomatoesResult | None:
    try:
        fandango_result = fandango_search(title, year, fandango_slug)

    except Exception as e:
        print(f"Error searching Fandango for {title} ({year}): {e}")
        return None

    if not fandango_result:
        print(f"No Fandango result found for {title} ({year})")
        return None

    url = f"https://www.fandango.com/napi/fanAndCriticReviews/{fandango_result['link_id']}/:pageSize"

    r = S.get(url, headers=headers)

    r.raise_for_status()

    data: FandangoReviewsResponse = r.json()

    if data["error"]:
        return None

    if not data["data"]["rottenTomatoesUrl"]:
        return None

    # Extract the Rotten Tomatoes slug from the URL
    rotten_tomatoes_slug = data["data"]["rottenTomatoesUrl"].split("/")[-1]

    popcorn_meter = data["data"]["audienceScore"]
    if popcorn_meter is None:
        popcorn_meter = 0
    else:
        popcorn_meter = int(popcorn_meter.rstrip("%"))

    # Ensure the tomato meter is also an integer
    tomato_meter = data["data"]["criticsScore"]
    if tomato_meter is None:
        tomato_meter = 0
    else:
        tomato_meter = int(tomato_meter.rstrip("%"))

    return RottenTomatoesResult(
        rotten_tomatoes_slug=rotten_tomatoes_slug,
        popcorn_meter=popcorn_meter,
        ratingCount=data["data"]["ratingCount"],
        tomato_meter=tomato_meter,
        fandango_slug=fandango_result["fandango_slug"],
    )
