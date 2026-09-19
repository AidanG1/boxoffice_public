# from session import S
import requests
import time
import random


S = requests.Session()
"""Requests session for general"""

from typing import TypedDict
from bs4 import BeautifulSoup


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
]


def make_request_with_retry(url: str) -> requests.Response | None:
    max_retries = 3
    base_delay = 2

    for attempt in range(max_retries):
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            r = S.get(url, headers=headers)
            r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                # print(f"Got 403 for {url}, attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    sleep_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(sleep_time)
                    continue
                else:
                    return None
            raise
    return None


def get_letterboxd_id(tmdb_id: int) -> str | None:
    # https://letterboxd.com/tmdb/1087891
    url = f"https://letterboxd.com/tmdb/{tmdb_id}/"

    r = make_request_with_retry(url)
    if r is None:
        return None

    # should redirect to https://letterboxd.com/film/the-amateur-2025/
    if r.url.startswith("https://letterboxd.com/film/"):
        # Extract the Letterboxd ID from the URL
        parts = r.url.split("/")
        if len(parts) > 4:
            return parts[4]
        # otherwise, return None
    return None


class LetterboxdResult(TypedDict):
    watched_count: int
    listed_count: int
    liked_count: int
    average_rating: int  # 2.93 multiplied by 100
    rating_count: int
    per_each_rating_counts: list[
        int
    ]  # 10 numbers representing the count of ratings from 0.5 to 5.0 in increments of 0.5


def get_letterboxd_values(letterboxd_id: str) -> LetterboxdResult | None:
    # https://letterboxd.com/csi/film/the-amateur-2025/ratings-summary/
    # https://letterboxd.com/csi/film/the-amateur-2025/stats/
    url = f"https://letterboxd.com/csi/film/{letterboxd_id}/ratings-summary/"
    r = make_request_with_retry(url)
    if r is None:
        print(f"Could not get ratings summary for Letterboxd ID: {letterboxd_id} (403 Forbidden)")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    """<body><section class="section ratings-histogram-chart"> <h2 class="section-heading"><a href="/film/the-amateur-2025/ratings/" class="" title="">Ratings</a></h2> <a href="/film/the-amateur-2025/fans/" class="all-link more-link">71 fans</a> <span class="average-rating"> <a href="/film/the-amateur-2025/ratings/" title="Weighted average of 2.93 based on 119,515&nbsp;ratings" class="tooltip display-rating">2.9</a> </span> <div class="rating-histogram clear rating-histogram-exploded"> <span class="rating-green rating-green-tiny rating-1"><span class="rating rated-2">★</span></span> <ul> <li class="rating-histogram-bar" style="width: 15px; left: 0px"> <a href="/film/the-amateur-2025/ratings/rated/%C2%BD/by/rating/" class="ir tooltip" title="471&nbsp;half-★ ratings (0%)">471&nbsp;half-★ ratings (0%)<i style="height: 1.51533039871759px;"></i></a> </li> <li class="rating-histogram-bar" style="width: 15px; left: 16px"> <a href="/film/the-amateur-2025/ratings/rated/1/by/rating/" class="ir tooltip" title="1,578&nbsp;★ ratings (1%)">1,578&nbsp;★ ratings (1%)<i style="height: 2.7265209536653012px;"></i></a> </li> <li class="rating-histogram-bar" style="width: 15px; left: 32px"> <a href="/film/the-amateur-2025/ratings/rated/1%C2%BD/by/rating/" class="ir tooltip" title="2,743&nbsp;★½ ratings (2%)">2,743&nbsp;★½ ratings (2%)<i style="height: 4.001170453678023px;"></i></a> </li> <li class="rating-histogram-bar" style="width: 15px; left: 48px"> <a href="/film/the-amateur-2025/ratings/rated/2/by/rating/" class="ir tooltip" title="10,694&nbsp;★★ ratings (9%)">10,694&nbsp;★★ ratings (9%)<i style="height: 12.700516526297042px;"></i></a> </li> <li class="rating-histogram-bar" style="width: 15px; left: 64px"> <a href="/film/the-amateur-2025/ratings/rated/2%C2%BD/by/rating/" class="ir tooltip" title="19,053&nbsp;★★½ ratings (16%)">19,053&nbsp;★★½ ratings (16%)<i style="height: 21.846263453856135px;"></i></a> </li> <li class="rating-histogram-bar" style="width: 15px; left: 80px"> <a href="/film/the-amateur-2025/ratings/rated/3/by/rating/" class="ir tooltip" title="39,301&nbsp;★★★ ratings (33%)">39,301&nbsp;★★★ ratings (33%)<i style="height: 44.0px;"></i></a> </li> <li class="rating-histogram-bar" style="width: 15px; left: 96px"> <a href="/film/the-amateur-2025/ratings/rated/3%C2%BD/by/rating/" class="ir tooltip" title="24,944&nbsp;★★★½ ratings (21%)">24,944&nbsp;★★★½ ratings (21%)<i style="height: 28.291722856924757px;"></i></a> </li> <li class="rating-histogram-bar" style="width: 15px; left: 112px"> <a href="/film/the-amateur-2025/ratings/rated/4/by/rating/" class="ir tooltip" title="15,049&nbsp;★★★★ ratings (13%)">15,049&nbsp;★★★★ ratings (13%)<i style="height: 17.465408004885372px;"></i></a> </li> <li class="rating-histogram-bar" style="width: 15px; left: 128px"> <a href="/film/the-amateur-2025/ratings/rated/4%C2%BD/by/rating/" class="ir tooltip" title="2,638&nbsp;★★★★½ ratings (2%)">2,638&nbsp;★★★★½ ratings (2%)<i style="height: 3.886287880715503px;"></i></a> </li> <li class="rating-histogram-bar" style="width: 15px; left: 144px"> <a href="/film/the-amateur-2025/ratings/rated/5/by/rating/" class="ir tooltip" title="3,044&nbsp;★★★★★ ratings (3%)">3,044&nbsp;★★★★★ ratings (3%)<i style="height: 4.330500496170581px;"></i></a> </li> </ul> <span class="rating-green rating-green-tiny rating-5"><span class="rating rated-10">★★★★★</span></span> </div> </section></body>"""

    ratings_summary = soup.find("section", class_="ratings-histogram-chart")
    if not ratings_summary:
        print(f"No ratings summary found for Letterboxd ID: {letterboxd_id}")
        return None

    average_rating = ratings_summary.find("span", class_="average-rating")

    if not average_rating:
        print(f"No average rating found for Letterboxd ID: {letterboxd_id}")
        return None

    average_rating_tooltip = average_rating.find("a", class_="tooltip")
    if not average_rating_tooltip:
        print(f"No average rating tooltip found for Letterboxd ID: {letterboxd_id}")
        return None

    average_rating_tooltip_text = average_rating_tooltip.get("title", "")
    if not average_rating_tooltip_text:
        print(
            f"No average rating tooltip text found for Letterboxd ID: {letterboxd_id}"
        )
        return None

    average_rating_tooltip_text = str(average_rating_tooltip_text).replace("\xa0", " ")

    # Weighted average of 2.93 based on 119,515 ratings <-- tooltip text
    split_text = average_rating_tooltip_text.split(" ")
    average_rating_value = split_text[
        3
    ]  # This should be the average rating value, e.g., '2.93'
    average_rating_value = int(float(average_rating_value) * 100)
    rating_count = int(split_text[-2].replace(",", ""))

    # Get the per-each-rating counts
    rating_histogram = ratings_summary.find("div", class_="rating-histogram")
    if not rating_histogram:
        print(f"No rating histogram found for Letterboxd ID: {letterboxd_id}")
        return None

    per_each_rating_counts = []
    for bar in rating_histogram.find_all("li", class_="rating-histogram-bar"):
        bar_a = bar.find("a", class_="bar ir tooltip")
        if not bar_a:
            print(
                f"No bar found in rating histogram for Letterboxd ID: {letterboxd_id}"
            )
            print(BeautifulSoup(str(bar), "html.parser").prettify())
            continue
        count_text = bar_a.get("title", "")
        count_text = str(count_text).replace("\xa0", " ")
        if count_text:
            count = int(count_text.split(" ")[0].replace(",", ""))
            per_each_rating_counts.append(count)

    if len(per_each_rating_counts) != 10:
        print(
            f"Expected 10 rating counts, but found: {len(per_each_rating_counts)} for Letterboxd ID: {letterboxd_id}"
        )
        return None

    # https://letterboxd.com/csi/film/the-amateur-2025/stats/
    url = f"https://letterboxd.com/csi/film/{letterboxd_id}/stats/"
    r = make_request_with_retry(url)
    if r is None:
        print(f"Could not get stats for Letterboxd ID: {letterboxd_id} (403 Forbidden)")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    """<body><div class="production-statistic-list" aria-label="Statistics for The Amateur (2025)"> <div class="production-statistic -watches" aria-label="Watched by 132,866&nbsp;members"> <a class="tooltip" href="/film/the-amateur-2025/members/" title="Watched by 132,866&nbsp;members" data-html="true"> <svg xmlns="http://www.w3.org/2000/svg" role="presentation" class="glyph" width="16" height="11" viewBox="0 0 16 11"><path fill="#000" fill-rule="evenodd" d="M8.009 1c4.046 0 7.51 3.873 7.945 4.378l.04.048L16 5.6S12.324 10 7.991 10C3.945 10 .481 6.127.046 5.622L0 5.568V5.4S3.676 1 8.009 1ZM8 2.625a2.875 2.875 0 1 0 0 5.75 2.875 2.875 0 0 0 0-5.75ZM8 4.25a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5Z"></path></svg> <span class="label">133K</span> </a> </div> <div class="production-statistic -lists" aria-label="Appears in 28,098&nbsp;lists"> <a class="tooltip" href="/film/the-amateur-2025/lists/by/popular/" title="Appears in 28,098&nbsp;lists" data-html="true"> <svg xmlns="http://www.w3.org/2000/svg" role="presentation" class="glyph" width="10" height="10" viewBox="0 0 10 10"><path fill="#000" fill-rule="evenodd" d="M10 .75v2.5a.75.75 0 0 1-.75.75h-2.5A.75.75 0 0 1 6 3.25V.75A.75.75 0 0 1 6.75 0h2.5a.75.75 0 0 1 .75.75ZM6.75 6h2.5a.75.75 0 0 1 .75.75v2.5a.75.75 0 0 1-.75.75h-2.5A.75.75 0 0 1 6 9.25v-2.5A.75.75 0 0 1 6.75 6ZM4 .75v2.5a.75.75 0 0 1-.75.75H.75A.75.75 0 0 1 0 3.25V.75A.75.75 0 0 1 .75 0h2.5A.75.75 0 0 1 4 .75ZM.75 6h2.5a.75.75 0 0 1 .75.75v2.5a.75.75 0 0 1-.75.75H.75A.75.75 0 0 1 0 9.25v-2.5A.75.75 0 0 1 .75 6Z"></path></svg> <span class="label">28K</span> </a> </div> <div class="production-statistic -likes" aria-label="Liked by 25,113&nbsp;members"> <a class="tooltip" href="/film/the-amateur-2025/likes/" title="Liked by 25,113&nbsp;members" data-html="true"> <svg xmlns="http://www.w3.org/2000/svg" role="presentation" class="glyph" width="12" height="11" viewBox="0 0 12 11"><path fill="#000" fill-rule="evenodd" d="M6 2.25S4.51.5 2.99.5C1.46.5 0 1.23 0 3.37c0 1.52 1.5 2.86 1.5 2.86l3.812 3.617a1 1 0 0 0 1.376 0L10.5 6.23S12 4.89 12 3.37C12 1.23 10.54.5 9.01.5 7.49.5 6 2.25 6 2.25Z"></path></svg> <span class="label">25K</span> </a> </div> </div></body>"""
    production_statistic_list = soup.find("div", class_="production-statistic-list")
    if not production_statistic_list:
        print(f"No production statistic list found for Letterboxd ID: {letterboxd_id}")
        return None

    watched_count = production_statistic_list.find("div", class_="-watches")

    if not watched_count:
        print(f"No watched count found for Letterboxd ID: {letterboxd_id}")
        return None

    # get the aria-label attribute
    watched_count_text = watched_count.get("aria-label", "")
    watched_count_text = str(watched_count_text).replace("\xa0", " ")
    if not watched_count_text:
        print(f"No watched count text found for Letterboxd ID: {letterboxd_id}")
        return None

    # Watched by 132,866 members
    watched_count_value = int(watched_count_text.split(" ")[2].replace(",", ""))

    listed_count = production_statistic_list.find("div", class_="-lists")
    if not listed_count:
        print(f"No listed count found for Letterboxd ID: {letterboxd_id}")
        return None

    listed_count_text = listed_count.get("aria-label", "")
    listed_count_text = str(listed_count_text).replace("\xa0", " ")
    if not listed_count_text:
        print(f"No listed count text found for Letterboxd ID: {letterboxd_id}")
        return None

    # Appears in 28,098 lists
    listed_count_value = int(listed_count_text.split(" ")[2].replace(",", ""))

    liked_count = production_statistic_list.find("div", class_="-likes")
    if not liked_count:
        print(f"No liked count found for Letterboxd ID: {letterboxd_id}")
        return None

    liked_count_text = liked_count.get("aria-label", "")
    liked_count_text = str(liked_count_text).replace("\xa0", " ")
    if not liked_count_text:
        print(f"No liked count text found for Letterboxd ID: {letterboxd_id}")
        return None

    # Liked by 25,113 members
    liked_count_value = int(liked_count_text.split(" ")[2].replace(",", ""))

    return LetterboxdResult(
        watched_count=watched_count_value,
        listed_count=listed_count_value,
        liked_count=liked_count_value,
        average_rating=average_rating_value,
        rating_count=rating_count,
        per_each_rating_counts=per_each_rating_counts,
    )


if __name__ == "__main__":
    # Example usage
    tmdb_id = "1087891"  # Replace with a valid TMDB ID
    letterboxd_id = get_letterboxd_id(tmdb_id)
    if letterboxd_id:
        print(f"Letterboxd ID for TMDB ID {tmdb_id}: {letterboxd_id}")
    else:
        print(f"No Letterboxd ID found for TMDB ID {tmdb_id}.")

    if letterboxd_id:
        letterboxd_values = get_letterboxd_values(letterboxd_id)
        if letterboxd_values:
            print(f"Letterboxd values for ID {letterboxd_id}: {letterboxd_values}")
        else:
            print(f"No Letterboxd values found for ID {letterboxd_id}.")
    else:
        print("No Letterboxd ID to fetch values for.")
