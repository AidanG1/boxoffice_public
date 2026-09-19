import re
from pydantic import BaseModel
from session import WS


class ScrapeThumbnail(BaseModel):
    mimetype: str
    width: int
    height: int
    duration: int | None
    url: str


class ScrapeResult(BaseModel):
    id: int
    key: str
    title: str
    excerpt: str
    matched_title: str | None
    description: str | None
    thumbnail: ScrapeThumbnail | None


class ScrapeResults(BaseModel):
    pages: list[ScrapeResult]


LANGUAGE_CODE = "en"

BASE_URL = "https://api.wikimedia.org/core/v1/wikipedia/"
ENDPOINT = "/search/page"


def get_wikipedia_information(movie_title: str, movie_year: int) -> ScrapeResult | None:
    movie_title = movie_title.replace("&", "and")

    url = f"{BASE_URL}{LANGUAGE_CODE}{ENDPOINT}?q={movie_title} {movie_year}&limit=15"

    r = WS.get(url)
    data = r.json()

    # convert data to a ScrapeResults object
    data = ScrapeResults(**data)

    results = data.pages

    if len(results) == 0:
        print(f"No results for {movie_title}")
        raise Exception("No results found")

    # first priority is a match with "title (year film)"
    for res in results:
        if f"{movie_title}" in res.title and (
            f"({movie_year} film)" in res.title
            or f"({movie_year - 1} film)" in res.title
        ):
            return res

    # second priority is description check
    raw = r"(\d{4}).*film"

    for res in results:
        if res.description is None:
            continue
        match = re.match(raw, res.description)
        if match is not None:
            if (
                int(match.group(1)) == movie_year
                or int(match.group(1)) == movie_year - 1
            ):  # sometimes the year is off by one
                return res

    # next check for film) in page key, just pick the first one
    for res in results:
        if "film)" in res.key:
            return res
    # then search for the year
    for res in results:
        if str(movie_year) in res.key:
            return res
    # then see if there is a result with (film) in the top 10
    for res in results[:10]:
        if "(film)" in res.key:
            return res
    # then search for just the title
    for res in results:
        if movie_title in res.key:
            return res

    # print the wikipedia search results if no match is found
    print(f"Search results for {movie_title} {movie_year} {url}")
    return None


def wikidata_id_to_wikipedia_id(wikidata_id: str) -> str | None:
    url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=sitelinks&ids={wikidata_id}&sitefilter=enwiki"

    """{"entities":{"Q740528":{"type":"item","id":"Q740528","sitelinks":{"enwiki":{"site":"enwiki","title":"Wild Wild West","badges":[]}}}},"success":1}"""

    wiki_data = WS.get(url).json()

    if (
        "entities" not in wiki_data
        or wikidata_id not in wiki_data["entities"]
        or "enwiki" not in wiki_data["entities"][wikidata_id]["sitelinks"]
    ):
        return None

    return wiki_data["entities"][wikidata_id]["sitelinks"]["enwiki"]["title"]