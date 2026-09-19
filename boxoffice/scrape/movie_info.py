import time
import json
import re
from urllib.parse import quote_plus
from typing import Any
import requests
from scrape.box_office_mojo_scrape import scrape_box_office_mojo_totals
from scrape.rotten_tomatoes_search_fandango import get_rotten_tomatoes
from scrape.letterboxd_search import get_letterboxd_values
from scrape.scrape_types import (
    MovieDetails,
    MovieInfoDay,
    TMdBMovieInfo,
    IMdBMovieInfo,
    YoutubeMovieInfo,
)
import datetime as dt
from session import TS, S, WS, scraper
from database.types import Movie
from bs4 import BeautifulSoup, Tag
from colors import bcolors

try:
    from yt_dlp import YoutubeDL
except Exception:
    YoutubeDL = None


def scrape_tmdb_stats(tmdb_id: int) -> TMdBMovieInfo:
    r = TS.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}?language=en-US")

    data = r.json()

    data = MovieDetails(**data)

    return TMdBMovieInfo(
        tmdb_popularity=data.popularity,
        tmdb_vote_average=data.vote_average,
        tmdb_vote_count=data.vote_count,
    )


def scrape_imdb_stats(imdb_id: str) -> IMdBMovieInfo:
    metacritic_rating: int | None = None
    imdb_rating_value = 0
    imdb_votes_value = 0

    try:
        import os
        # Try OMDb API first, as it bypasses AWS WAF entirely and provides exactly what's needed
        omdb_key = os.getenv("OMDB_KEY", "")
        omdb_url = f"https://www.omdbapi.com/?apikey={omdb_key}&i={imdb_id}"
        omdb_res = S.get(omdb_url, timeout=10)
        
        if omdb_res.status_code == 200:
            data = omdb_res.json()
            if data.get("Response") == "True":
                imdb_rating_str = data.get("imdbRating", "N/A")
                if imdb_rating_str != "N/A":
                    try:
                        imdb_rating_value = int(float(imdb_rating_str) * 10)
                    except ValueError:
                        pass
                
                imdb_votes_str = data.get("imdbVotes", "N/A")
                if imdb_votes_str != "N/A":
                    try:
                        imdb_votes_value = int(imdb_votes_str.replace(",", ""))
                    except ValueError:
                        pass
                
                metascore_str = data.get("Metascore", "N/A")
                if metascore_str != "N/A":
                    try:
                        metacritic_rating = int(metascore_str)
                    except ValueError:
                        pass
                
                if imdb_rating_value > 0 and imdb_votes_value > 0:
                    return IMdBMovieInfo(
                        imdb_rating=imdb_rating_value,
                        imdb_votes=imdb_votes_value,
                        metacritic_rating=metacritic_rating,
                    )
    except Exception as e:
        print(f"OMDb API fallback failed for {imdb_id}: {e}")

    # Fallback to pure scraping
    # https://m.imdb.com/title/tt0088258/
    url = f"https://www.imdb.com/title/{imdb_id}/"
    r = S.get(url)

    soup = BeautifulSoup(r.text, "html.parser")

    def parse_compact_number(value: str | None) -> int:
        if value is None:
            return 0
        text = value.strip().replace(",", "")
        if text == "":
            return 0
        multiplier = 1
        suffix = text[-1].upper()
        if suffix == "K":
            multiplier = 1000
            text = text[:-1]
        elif suffix == "M":
            multiplier = 1000000
            text = text[:-1]
        elif suffix == "B":
            multiplier = 1000000000
            text = text[:-1]
        try:
            return int(float(text) * multiplier)
        except ValueError:
            return 0

    metacritic_rating: int | None = None
    imdb_rating_value = 0
    imdb_votes_value = 0

    metacritic_rating_tag = soup.find(attrs={"data-testid": "metacritic-score-box"})
    if metacritic_rating_tag is None:
        metacritic_rating_tag = soup.find(class_="metacritic-score-box")
    if metacritic_rating_tag is not None:
        metacritic_match = re.search(r"(\d{1,3})", metacritic_rating_tag.get_text(" ", strip=True))
        if metacritic_match is not None:
            metacritic_rating = int(metacritic_match.group(1))

    json_ld_rating_value: str | None = None
    json_ld_rating_count: str | None = None
    json_ld_scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    for script in json_ld_scripts:
        script_text = script.string or script.get_text(strip=True)
        if not script_text:
            continue
        try:
            payload = json.loads(script_text)
        except (json.JSONDecodeError, TypeError):
            continue

        objects = payload if isinstance(payload, list) else [payload]
        for obj in objects:
            if not isinstance(obj, dict):
                continue
            aggregate_rating = obj.get("aggregateRating")
            if not isinstance(aggregate_rating, dict):
                continue
            rating_value = aggregate_rating.get("ratingValue")
            rating_count = aggregate_rating.get("ratingCount")
            if rating_value is not None:
                json_ld_rating_value = str(rating_value)
            if rating_count is not None:
                json_ld_rating_count = str(rating_count)
            if json_ld_rating_value is not None and json_ld_rating_count is not None:
                break
        if json_ld_rating_value is not None and json_ld_rating_count is not None:
            break

    if json_ld_rating_value is not None:
        try:
            imdb_rating_value = int(float(json_ld_rating_value) * 10)
        except ValueError:
            imdb_rating_value = 0

    if json_ld_rating_count is not None:
        imdb_votes_value = parse_compact_number(json_ld_rating_count)

    if imdb_rating_value == 0:
        imdb_rating_div = soup.find(
            "div", {"data-testid": "hero-rating-bar__aggregate-rating__score"}
        )
        if imdb_rating_div is not None:
            imdb_rating_match = re.search(
                r"(\d+(?:\.\d+)?)", imdb_rating_div.get_text(" ", strip=True)
            )
            if imdb_rating_match is not None:
                imdb_rating_value = int(float(imdb_rating_match.group(1)) * 10)

    if imdb_votes_value == 0:
        votes_label_tag = soup.find(
            attrs={"aria-label": re.compile(r"ratings?", re.IGNORECASE)}
        )
        if votes_label_tag is not None:
            votes_match = re.search(
                r"([\d.,]+\s*[KMBkmb]?)", votes_label_tag.get("aria-label", "")
            )
            if votes_match is not None:
                imdb_votes_value = parse_compact_number(votes_match.group(1).replace(" ", ""))

    if imdb_rating_value == 0:
        print(f"Failed to find IMDb rating for {url}")

    return IMdBMovieInfo(
        imdb_rating=imdb_rating_value,
        imdb_votes=imdb_votes_value,
        metacritic_rating=metacritic_rating,
    )


def get_wikipedia_views(wikipedia_key: str, date: dt.date) -> int:
    r = WS.get(
        f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{wikipedia_key}/daily/{date.strftime('%Y%m%d')}/{date.strftime('%Y%m%d')}"
    )

    data = r.json()

    if "items" not in data or len(data["items"]) == 0:
        print(
            f"{bcolors.FAIL} Failed to get items for {wikipedia_key} on {date} with url {r.url}{bcolors.ENDC}"
        )
        return 0

    return data["items"][0]["views"]


def get_wikipedia_views_range(
    wikipedia_key: str, start_date: dt.date, end_date: dt.date, retries: int = 0
) -> dict[str, int]:
    if wikipedia_key is None:
        return {}
    # within wikipedia key, replace ? with %3F
    wikipedia_key = (
        wikipedia_key.replace("?", "%3F").replace("&", "%26").replace("!", "%21")
    )

    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{wikipedia_key}/daily/{start_date.strftime('%Y%m%d')}/{end_date.strftime('%Y%m%d')}"
    r = WS.get(url)

    data = r.json()

    if "items" not in data:
        print(
            f"{bcolors.FAIL} Retrying {retries + 1} -> Failed to get items for {wikipedia_key} from {start_date} to {end_date} with url {url}{bcolors.ENDC}"
        )

        if (
            retries < 0
        ):  # only retry once cause normally retries are cause the page has no data and not a network error or rate limit
            time.sleep(2)
            return get_wikipedia_views_range(
                wikipedia_key, start_date, end_date, retries + 1
            )
        else:
            return {}

    return {item["timestamp"]: item["views"] for item in data["items"]}


def get_hsx_price(hsx_id: int, date: dt.date) -> float | None:
    # https://www.hsx.com/chart/detail_chart_data.php?id=42684
    r = S.get(f"https://www.hsx.com/chart/detail_chart_data.php?id={hsx_id}")
    """Date,Close 2024-02-01,41.32 2024-02-02,41.38 2024-02-03,41.29 2024-02-04,41.29 2024-02-05,41.72 2024-02-06,41.88 2024-02-07,42.13"""
    data = r.text

    data = data.replace("\n", " ")

    pairs = data.split(" ")

    for pair in pairs:
        pair_split = pair.split(",")
        if len(pair_split) != 2:
            continue
        date_str, price_str = pair_split

        if date_str == date.strftime("%Y-%m-%d"):
            return float(price_str)

    return None


def get_youtube_trailer_views(
    title: str, release_year: int, retries: int = 0
) -> YoutubeMovieInfo:
    def summarize_views(views: list[int]) -> YoutubeMovieInfo:
        if len(views) == 0:
            return YoutubeMovieInfo(
                youtube_sum_1_views=0,
                youtube_sum_3_views=0,
                youtube_sum_all_views=0,
            )

        return YoutubeMovieInfo(
            youtube_sum_1_views=max(views),
            youtube_sum_3_views=sum(views[:3]),
            youtube_sum_all_views=sum(views),
        )

    def scrape_youtube_views_without_api(search_title: str, year: int) -> list[int]:
        query = f"{search_title} {year} movie trailer"
        search_url = (
            "https://www.youtube.com/results?search_query=" + quote_plus(query)
        )

        try:
            search_response = S.get(search_url)
        except Exception as e:
            print(f"Failed YouTube search request for {query}: {e}")
            return []

        if search_response.status_code != 200:
            print(
                f"Failed YouTube search request for {query} with status {search_response.status_code}"
            )
            return []

        video_ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", search_response.text)

        deduped_video_ids: list[str] = []
        seen: set[str] = set()
        for vid in video_ids:
            if vid in seen:
                continue
            seen.add(vid)
            deduped_video_ids.append(vid)
            if len(deduped_video_ids) >= 10:
                break

        views: list[int] = []
        for video_id in deduped_video_ids:
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            try:
                watch_response = S.get(watch_url)
            except Exception as e:
                print(f"Failed watch request for {watch_url}: {e}")
                continue

            if watch_response.status_code != 200:
                continue

            soup = BeautifulSoup(watch_response.text, "html.parser")
            og_title_tag = soup.find("meta", attrs={"property": "og:title"})
            video_title = ""
            if isinstance(og_title_tag, Tag):
                content_attr = og_title_tag.attrs.get("content")
                if isinstance(content_attr, str):
                    video_title = content_attr.lower()

            if "trailer" not in video_title:
                continue

            view_match = re.search(r'"viewCount":"(\\d+)"', watch_response.text)
            if view_match is None:
                view_match = re.search(
                    r'"interactionCount":"(\\d+)"', watch_response.text
                )

            if view_match is None:
                continue

            views.append(int(view_match.group(1)))

        return views

    def scrape_youtube_views_with_ytdlp(search_title: str, year: int) -> list[int]:
        if YoutubeDL is None:
            return []

        query = f"ytsearch10:{search_title} {year} movie trailer"
        options: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
            "extract_flat": False,
            "ignoreerrors": True,
            "socket_timeout": 15,
        }

        try:
            with YoutubeDL(options) as ydl:
                search_result = ydl.extract_info(query, download=False)
        except Exception as e:
            print(f"yt-dlp search failed for {search_title} ({year}): {e}")
            return []

        if not isinstance(search_result, dict):
            return []

        entries = search_result.get("entries", [])
        if not isinstance(entries, list):
            return []

        views: list[int] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            entry_title = str(entry.get("title") or "").lower()
            if "trailer" not in entry_title:
                continue

            view_count = entry.get("view_count")
            if isinstance(view_count, int):
                views.append(view_count)
                continue

            webpage_url = entry.get("webpage_url")
            if not isinstance(webpage_url, str):
                video_id = entry.get("id")
                if isinstance(video_id, str):
                    webpage_url = f"https://www.youtube.com/watch?v={video_id}"

            if not isinstance(webpage_url, str):
                continue

            try:
                with YoutubeDL(options) as ydl:
                    video_info = ydl.extract_info(webpage_url, download=False)
            except Exception:
                continue

            if not isinstance(video_info, dict):
                continue

            detailed_views = video_info.get("view_count")
            if isinstance(detailed_views, int):
                views.append(detailed_views)

        return views

    raw_title = title

    # replace ? with %3F
    title = (
        title.replace("?", "%3F")
        .replace("!", "%21")
        .replace("&", "%26")
        .replace("...", "")
    )

    base_urls = [
        "https://pipedapi.wireway.ch/search?q=",
        "https://pipedapi.kavin.rocks/search?q=",
    ]

    current_base = base_urls[retries % len(base_urls)]

    piped_url = f"{current_base}{title} {release_year} movie trailer&filter=videos"

    views: list[int] = []

    response = scraper.get(piped_url)

    if response.status_code != 200:
        print(f"Failed to get response for {piped_url}")

    try:
        piped_response = response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Failed to decode JSON for {piped_url}")
        print(response.text)
        piped_response = {}

    if "items" not in piped_response:
        print(f"Failed to get items for {piped_url}")

        if retries < 0:
            print(f"Retrying {retries + 1}")
            time.sleep(retries * 2 + 1.1)
            return get_youtube_trailer_views(title, release_year, retries + 1)
        else:
            fallback_views = scrape_youtube_views_with_ytdlp(raw_title, release_year)
            if len(fallback_views) == 0:
                fallback_views = scrape_youtube_views_without_api(raw_title, release_year)
            print(f"Fallback YouTube scrape views: {fallback_views}")
            return summarize_views(fallback_views)

    for item in piped_response["items"]:
        if "trailer" in item["title"].lower():
            views.append(item["views"])

    print(f"Url: {piped_url}")
    print(views)

    if len(views) == 0:
        fallback_views = scrape_youtube_views_with_ytdlp(raw_title, release_year)
        if len(fallback_views) == 0:
            fallback_views = scrape_youtube_views_without_api(raw_title, release_year)
        print(f"Fallback YouTube scrape views: {fallback_views}")
        return summarize_views(fallback_views)

    # need to get the max, first 3 sum, first 5 sum, and total sum
    return summarize_views(views)


def make_movie_info_day(movie: Movie, date: dt.date) -> MovieInfoDay:
    is_backfilled = True

    if date == dt.date.today() or date == dt.date.today() - dt.timedelta(days=1):
        is_backfilled = False

    tmdb_info = scrape_tmdb_stats(movie["tmdb_id"])
    imdb_info = scrape_imdb_stats(movie["imdb_id"])
    if movie["wikipedia_key"] is None:
        wikipedia_views = 0
    else:
        wikipedia_views = get_wikipedia_views(movie["wikipedia_key"], date)
    if movie["hsx_id"] is None:
        hsx_price = None
    else:
        hsx_price = get_hsx_price(movie["hsx_id"], date)

    release_year = int(movie["release_date"][:4])

    rt_info = get_rotten_tomatoes(
        movie["title"], release_year, movie["fandango_slug"]
    )

    if rt_info is None:
        print(f"Make Movie Info Day: No Rotten Tomatoes data found for {movie['title']} ({release_year})")

    try:
        letterboxd_info = get_letterboxd_values(movie["letterboxd_id"])
    except Exception as e:
        print(f"Error getting Letterboxd values for {movie['title']}: {e}")
        letterboxd_info = None

    release_date = dt.datetime.strptime(movie["release_date"], "%Y-%m-%d").date()

    youtube_info = get_youtube_trailer_views(movie["title"], release_date.year)

    bom_totals = scrape_box_office_mojo_totals(movie["imdb_id"])

    return MovieInfoDay(
        movie_id=movie["id"],
        date=date,
        is_backfilled=is_backfilled,
        tmdb_popularity=tmdb_info.tmdb_popularity,
        tmdb_vote_average=tmdb_info.tmdb_vote_average,
        tmdb_vote_count=tmdb_info.tmdb_vote_count,
        imdb_rating=imdb_info.imdb_rating,
        imdb_votes=imdb_info.imdb_votes,
        metacritic_rating=imdb_info.metacritic_rating,
        wikipedia_views=wikipedia_views,
        hsx_price=hsx_price,
        youtube_sum_1_views=youtube_info.youtube_sum_1_views,
        youtube_sum_3_views=youtube_info.youtube_sum_3_views,
        youtube_sum_all_views=youtube_info.youtube_sum_all_views,
        letterboxd_watched_count=(
            letterboxd_info["watched_count"] if letterboxd_info else 0
        ),
        letterboxd_listed_count=(
            letterboxd_info["listed_count"] if letterboxd_info else 0
        ),
        letterboxd_liked_count=letterboxd_info["liked_count"] if letterboxd_info else 0,
        letterboxd_rating_count=(
            letterboxd_info["rating_count"] if letterboxd_info else 0
        ),
        letterboxd_average_rating=(
            letterboxd_info["average_rating"] if letterboxd_info else 0
        ),
        letterboxd_per_each_rating_counts=(
            letterboxd_info["per_each_rating_counts"] if letterboxd_info else [0] * 10
        ),
        rt_popcorn_meter=rt_info["popcorn_meter"] if rt_info else 0,
        rt_tomato_meter=rt_info["tomato_meter"] if rt_info else 0,
        rt_user_review_count=rt_info["ratingCount"] if rt_info else 0,
        international_box_office=bom_totals.international_total if bom_totals else 0
    )
