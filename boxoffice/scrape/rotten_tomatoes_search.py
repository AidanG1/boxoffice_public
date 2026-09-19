"""curl 'https://79frdp12pn-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.25.2)%3B%20Browser%20(lite)^&x-algolia-api-key=175588f6e5f8319b27702e4cc4013561^&x-algolia-application-id=79FRDP12PN' \
  --compressed \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0' \
  -H 'Accept: */*' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'content-type: application/x-www-form-urlencoded' \
  -H 'x-algolia-usertoken: 26c93f9e2bc6b8b3edaaf3898e7d11f09992783adf30391d93e1a5e5540ba0cd' \
  -H 'Origin: https://www.rottentomatoes.com' \
  -H 'DNT: 1' \
  -H 'Sec-GPC: 1' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://www.rottentomatoes.com/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: cross-site' \
  -H 'Priority: u=0' \
  --data-raw '{"requests":[{"indexName":"content_rt","params":"analyticsTags=%5B%22header_search%22%5D^&clickAnalytics=true^&filters=isEmsSearchable%20%3D%201^&hitsPerPage=5","query":"superman"},{"indexName":"people_rt","params":"analyticsTags=%5B%22header_search%22%5D^&clickAnalytics=true^&filters=isEmsSearchable%20%3D%201^&hitsPerPage=5","query":"superman"}]}'"""

from platform import release
from session import S
from typing import TypedDict, List, Optional


class RottenTomatoes(TypedDict):
    dateCertified: str
    audienceScore: int
    criticsIconUrl: str
    wantToSeeCount: int
    audienceIconUrl: str
    verifiedHot: bool
    scoreSentiment: str
    certifiedFresh: bool
    criticsScore: int
    newAdjustedTMSScore: int


class CastCrewCredits(TypedDict):
    Producer: List[str]
    Screenwriter: List[str]
    Director: List[str]


class CastCrew(TypedDict):
    cast: List[str]
    crew: CastCrewCredits


class CastOrCrewRole(TypedDict):
    role: str
    emsId: str
    name: str
    personId: str


class Trailer(TypedDict):
    mpxId: str
    thumbnailUrl: str
    publicId: str
    title: str
    runTime: float


class MovieHit(TypedDict):
    emsId: str
    emsVersionId: str
    tmsId: str
    rtId: str
    type: str
    title: str
    titles: List[str]
    vanity: str
    description: str
    releaseYear: int
    rating: str
    genres: List[str]
    posterImageUrl: str
    rottenTomatoes: RottenTomatoes
    runTime: int
    castCrew: CastCrew
    cast: List[CastOrCrewRole]
    crew: List[CastOrCrewRole]
    titleType: str
    pageViews_popularity: int
    trailer: Optional[Trailer]
    typeId: int
    promotion: int
    updateDate: str
    isEmsSearchable: int
    objectID: str
    _highlightResult: dict


class MovieSearchResponse(TypedDict):
    hits: List[MovieHit]
    nbHits: int
    page: int
    nbPages: int
    hitsPerPage: int
    exhaustiveNbHits: bool
    exhaustiveTypo: bool
    exhaustive: dict
    query: str
    params: str
    index: str
    queryID: str
    renderingContent: dict
    processingTimeMS: int
    processingTimingMS: dict
    serverTimeMS: int


class RottenTomatoesSearchResponse(TypedDict):
    results: List[MovieSearchResponse]


class RottenTomatoesResult(TypedDict):
    rotten_tomatoes_slug: str

    popcorn_meter: int  # this is the classic popcorn meter
    want_to_see_count: int
    mpaa_rating: str
    tomato_meter: int  # this is the classic tomato meter

    rotten_tomatoes_title: str
    rotten_tomatoes_year: str


def get_rotten_tomatoes(
    title: str, year: int, rotten_tomatoes_vanity: str | None
) -> RottenTomatoesResult | None:
    return None
    url = (
        "https://79frdp12pn-dsn.algolia.net/1/indexes/*/queries?"
        "x-algolia-agent=Algolia%20for%20JavaScript%20(4.25.2)%3B%20Browser%20(lite)^&"
        "x-algolia-api-key=175588f6e5f8319b27702e4cc4013561^&"
        "x-algolia-application-id=79FRDP12PN"
    )

    data_string = '''{"requests":[{"indexName":"content_rt","params":"analyticsTags=%5B%22header_search%22%5D&clickAnalytics=true&filters=isEmsSearchable%20%3D%201&hitsPerPage=5","query":"elio"},{"indexName":"people_rt","params":"analyticsTags=%5B%22header_search%22%5D&clickAnalytics=true&filters=isEmsSearchable%20%3D%201&hitsPerPage=5","query":"'''
    data_string += title + '"}]}'

    r = S.post(url, data=data_string)
    r.raise_for_status()
    data: RottenTomatoesSearchResponse = r.json()
    if not data["results"]:
        return None
    for result in data["results"]:
        for hit in result["hits"]:
            if hit["titles"][0].lower() == title.lower() and hit["releaseYear"] == year:
                if (
                    not rotten_tomatoes_vanity
                    or hit["vanity"] == rotten_tomatoes_vanity
                ):
                    return {
                        "rotten_tomatoes_slug": hit["vanity"],
                        "popcorn_meter": hit["rottenTomatoes"]["audienceScore"],
                        "want_to_see_count": hit["rottenTomatoes"]["wantToSeeCount"],
                        "mpaa_rating": hit["rating"],
                        "tomato_meter": hit["rottenTomatoes"]["criticsScore"],
                        "rotten_tomatoes_title": hit["title"],
                        "rotten_tomatoes_year": str(hit["releaseYear"]),
                    }
    return None
