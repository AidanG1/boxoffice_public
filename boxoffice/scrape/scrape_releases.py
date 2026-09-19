# target to scrape: https://the-numbers.com/movies/release-schedule

from colors import bcolors
from scrape.scrape_types import ScrapeRelease
from session import S
from bs4 import BeautifulSoup, NavigableString
from pydantic.json import pydantic_encoder
import datetime as dt
import json


def scrape_releases(until_days: int) -> list[ScrapeRelease]:
    url = "https://the-numbers.com/movies/release-schedule"
    r = S.get(url)
    r.raise_for_status()

    # save the html to boxoffice/html/releases
    today = dt.datetime.now().strftime("%Y-%m-%d")
    with open(f"boxoffice/html/releases/releases_{today}.html", "w") as f:
        f.write(r.text)

    soup = BeautifulSoup(r.text, "html.parser")

    # find the only table on the page
    table = soup.find("table")

    if table is None:
        print(bcolors.FAIL + "No table found on page" + bcolors.ENDC)
        print(soup.prettify())
        return []

    if isinstance(table, NavigableString):
        print(bcolors.FAIL + "Table is a NavigableString" + bcolors.ENDC)
        print(soup.prettify())
        return []

    rows = table.find_all("tr")

    if not rows:
        print(bcolors.WARNING + "No rows found in table" + bcolors.ENDC)
        return []

    releases = []

    scrape_until_date: dt.datetime = dt.datetime.now() + dt.timedelta(days=until_days)
    current_scrape_date: str | None = None

    for row in rows:
        # check if the row has an id
        row_id = row.get("id")

        if row_id is not None:
            # the row id will be a date formatted as YYYY-MM-DD
            row_id_date = dt.datetime.strptime(row_id, "%Y-%m-%d")

            current_scrape_date = row_id_date.strftime("%Y-%m-%d")

            if row_id_date > scrape_until_date:
                break

        if current_scrape_date is None:
            continue

        """ the columns are as follows:
        0: release date
        1: title
        2: distributor
        3: domestic box office to date
        4: trailer

        we only need column 1
        """

        columns = row.find_all("td")

        if not columns:
            print("No columns found in row")
            continue

        if len(columns) < 2:
            # print("Not enough columns found in row")
            continue

        title_column = columns[1]

        """<td><b><a href="/movie/Red-One-(2024)#tab=summary">Red One</a></b> (IMAX)</td>"""

        title_a = title_column.find("a")

        if title_a is None:
            print("No title found in column")
            continue

        title = title_a.text

        title_href = title_a.get("href")

        if title_href is None:
            print("No href found in title")
            continue

        title_slug = title_href.split("/")[2]

        if "#" in title_slug:
            title_slug = title_slug.split("#")[0]

        # the release type is the text after the title in the column
        release_type = title_column.text.split(title)[1].strip()

        releases.append(
            ScrapeRelease(
                date=current_scrape_date,
                numbers_slug=title_slug,
                title=title,
                release_type=release_type,
            )
        )

    return releases


def write_releases_to_json(releases: list[ScrapeRelease]) -> None:
    releases_json = json.dumps(releases, indent=4, default=pydantic_encoder)

    today = dt.datetime.now().strftime("%Y-%m-%d")

    with open(f"boxoffice/json/releases_{today}.json", "w") as f:
        f.write(releases_json)
