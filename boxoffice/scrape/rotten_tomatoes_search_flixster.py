from session import S
from typing import TypedDict, List, Optional


class RottenTomatoesResult(TypedDict):
    rotten_tomatoes_slug: str

    user_liked_score: int  # this is the classic popcorn meter
    user_average_score: int  # it is a float but multiply by 10. This is out of 5
    user_review_count: int
    user_rating_count: int
    want_to_see_count: int
    mpaa_warning: str
    mpaa_description: str
    mpaa_rating: str

    critic_liked_score: int  # this is the classic tomato meter
    critic_average_score: int  # this is a float but multiply by 10. This is out of 10
    critic_review_count: int

    rotten_tomatoes_title: str
    rotten_tomatoes_year: str


class QualityRating(TypedDict):
    src: str
    value: str


class Description(TypedDict):
    length: int
    size: str
    lang: str
    type: str
    src: str
    desc: str


class IdInfo(TypedDict):
    type: str
    src: str
    value: str


class PersonId(TypedDict):
    type: str
    id: str


class CastMember(TypedDict):
    characterName: str
    name: str
    ids: List[IdInfo]
    role: str
    order: str


class AssetInfo(TypedDict):
    width: str
    lastModified: str
    category: str
    height: str


class Asset(TypedDict):
    src: str
    uri: str
    assetId: str
    info: AssetInfo
    s3Uri: str
    primary: str
    adminSelectedAsset: Optional[bool]


class RtMappingInfo(TypedDict):
    mappingType: str


class PersonInfo(TypedDict):
    name: str
    ids: List[IdInfo]
    role: str
    order: str


class UserRatingSummary(TypedDict):
    dtlLikedScore: int
    scoresCount: int
    dtlWtsCount: int
    cF: str
    avgScore: float
    reviewCount: int
    ratingsStartDate: str
    canVerifyRatings: bool
    wtsCount: int
    cFDate: str
    dtlScoreCount: int


class Release(TypedDict):
    date: str
    country: str
    medium: str
    type: str
    location: Optional[str]
    prgSvcId: Optional[str]
    distributors: Optional[List[str]]
    src: Optional[str]
    addedByClient: Optional[str]


class MovieInfo(TypedDict):
    pictureFormats: List[str]
    soundMixes: List[str]
    trailers: List[dict]
    officialUrl: str
    releases: List[Release]


class MpaaRating(TypedDict):
    warning: str
    description: str
    code: str
    ratingsBody: str


class Genre(TypedDict):
    genreId: str
    genre: str
    src: str


class SimpleGenre(TypedDict):
    genre: str
    src: str
    addedByClient: Optional[str]


class LicensingStudio(TypedDict):
    displayStudioId: str
    territorySet: str
    displayStudio: str


class HostAsset(TypedDict):
    type: str
    uri: str


class Host(TypedDict):
    name: str
    country: str
    hostId: str
    assets: List[HostAsset]
    label: str
    lastIngestDate: str


class ViewingOption(TypedDict):
    license: str
    price: str
    quality: str
    start: Optional[str]
    end: Optional[str]


class Title(TypedDict):
    length: int
    subType: str
    lang: str
    type: str
    title: str
    src: str


class OvdEntry(TypedDict):
    tmsId: str
    emsId: str
    rootId: str
    hostId: str
    videoId: str
    titles: List[Title]
    title: str
    url: str
    emsVersionId: str
    lastSeen: str
    expirationTime: int
    host: Host
    viewingOptions: List[ViewingOption]
    updatedAt: Optional[str]
    image: Optional[str]
    vuduId: Optional[str]


class Rating(TypedDict):
    warning: Optional[str]
    description: str
    code: str
    ratingsBody: str


class Tomatometer(TypedDict):
    rottenCount: int
    movieReleaseYear: int
    tomatometer: int
    numReviews: int
    movieId: str
    mediaType: str
    pendingCertified: bool
    title: str
    consensus: str
    avgScore: float
    lastUpdate: str
    tomatometerState: str
    certifiedFresh: bool
    freshCount: int
    newAdjustedTMScore: int


class RtInfo(TypedDict):
    actors: List
    releaseDate: str
    director: dict
    vanityUrl: str
    movieId: str
    title: str
    releaseYear: int
    status: str


class Award(TypedDict):
    result: str
    name: str
    ids: List
    category: str
    year: str


class ExternalResource(TypedDict):
    type: str
    uri: str


class Movie(TypedDict):
    titleType: str
    releaseDateUsTheatrical: str
    emsId: str
    subject_keywords: List[str]
    connectorId: str
    titleId: str
    qualityRatings: List[QualityRating]
    emsCreateDate: str
    descriptions: List[Description]
    setting_keywords: List[str]
    emsVersionId: str
    cast: List[CastMember]
    assets: List[Asset]
    runTime: str
    character_keywords: List[str]
    originalAudioLang: str
    rtMappingInfo: RtMappingInfo
    director: PersonInfo
    countries: List[str]
    homeReleaseDate: str
    versionId: str
    top3Cast: List[CastMember]
    ovdReleaseDate: str
    releaseDateUs: str
    ids: List[PersonId]
    suggestSearch: str
    userRatingSummary: UserRatingSummary
    movieInfo: MovieInfo
    mpaaRating: MpaaRating
    advisories: List[str]
    totalGross: str
    primaryImageUrl: str
    lastIngestDate: str
    rt_id: int
    rootId: str
    originalGenres: List[Genre]
    titleLang: str
    title: str
    heroImageUrl: str
    vanity: str
    mainTitleId: str
    crew: List[PersonInfo]
    mood_keywords: List[str]
    provider: str
    ratings: List[Rating]
    genres: List[SimpleGenre]
    licensingStudios: List[LicensingStudio]
    ovd: List[OvdEntry]
    releaseYear: str
    theme_keywords: List[str]
    pageViews_popularity: int
    lastUpdatedTimestamp: str
    programType: str
    fullTitle: str
    latestShowDate: str
    posterArt: List[Asset]
    src: str
    altFilmId: str
    tomatometer: Tomatometer
    externalId: str
    time_period_keywords: List[str]
    suggest: List[str]
    titles: List[Title]
    url: str
    rt_info: RtInfo
    awards: List[Award]
    TMSId: str
    mainTitle: str
    aka: List[str]
    colorCode: str
    externalResources: List[ExternalResource]
    productionCompanies: List[str]
    user: str
    fandangoIds: List[str]
    sluggedTitle: str


def get_rotten_tomatoes(
    title: str, year: int, rotten_tomatoes_vanity: str | None
) -> RottenTomatoesResult | None:
    # https://www.flixster.com/api/ems/v2/search/movies?query=dune&size=18&page=0
    url = f"https://www.flixster.com/api/ems/v2/search/movies?query={title}&size=18&page=0"
    # print(f"Requesting Rotten Tomatoes for: {title} ({year}) with URL: {url}")
    r = S.get(url)
    r.raise_for_status()

    # Check if the response is empty
    if r.status_code == 204 or not r.text:
        print(
            f"Rotten Tomatoes: no results found for {title} ({year}) with vanity {rotten_tomatoes_vanity}"
        )
        return None

    try:
        # Attempt to parse the JSON response
        results: List[Movie] = r.json()
    except ValueError:
        print(
            f"Rotten Tomatoes: invalid JSON response for {title} ({year}) with vanity {rotten_tomatoes_vanity}"
        )
        return None

    if not results:
        return None

    # Filter results by year
    for result in results:

        if (
            rotten_tomatoes_vanity is None
            and result["releaseYear"] in (str(year), str(year - 1), str(year + 1))
        ) or (
            rotten_tomatoes_vanity is not None
            and result["vanity"] == rotten_tomatoes_vanity
        ):
            rt_result: RottenTomatoesResult = {
                "rotten_tomatoes_slug": result["vanity"],
                "user_liked_score": (
                    result["userRatingSummary"]["dtlLikedScore"]
                    if "userRatingSummary" in result
                    and "dtlLikedScore" in result["userRatingSummary"]
                    else 0
                ),
                "user_average_score": (
                    int(result["userRatingSummary"]["avgScore"] * 10)
                    if "userRatingSummary" in result
                    and "avgScore" in result["userRatingSummary"]
                    else 0
                ),
                "user_review_count": (
                    result["userRatingSummary"]["reviewCount"]
                    if "userRatingSummary" in result
                    and "reviewCount" in result["userRatingSummary"]
                    else 0
                ),
                "user_rating_count": (
                    result["userRatingSummary"]["scoresCount"]
                    if "userRatingSummary" in result
                    and "scoresCount" in result["userRatingSummary"]
                    else 0
                ),
                "want_to_see_count": (
                    result["userRatingSummary"]["wtsCount"]
                    if "userRatingSummary" in result
                    and "wtsCount" in result["userRatingSummary"]
                    else 0
                ),
                "mpaa_warning": (
                    result["mpaaRating"]["warning"]
                    if "mpaaRating" in result and "warning" in result["mpaaRating"]
                    else ""
                ),
                "mpaa_description": (
                    result["mpaaRating"]["description"]
                    if "mpaaRating" in result and "description" in result["mpaaRating"]
                    else ""
                ),
                "mpaa_rating": (
                    result["mpaaRating"]["code"]
                    if "mpaaRating" in result and "code" in result["mpaaRating"]
                    else ""
                ),
                "critic_liked_score": (
                    result["tomatometer"]["tomatometer"]
                    if "tomatometer" in result
                    else 0
                ),
                "critic_average_score": (
                    int(result["tomatometer"]["avgScore"] * 10)
                    if "tomatometer" in result and "avgScore" in result["tomatometer"]
                    else 0
                ),
                "critic_review_count": (
                    result["tomatometer"]["numReviews"]
                    if "tomatometer" in result and "numReviews" in result["tomatometer"]
                    else 0
                ),
                "rotten_tomatoes_title": result["title"],
                "rotten_tomatoes_year": result["releaseYear"],
            }
            return rt_result

    # If no exact match, return None
    return None
