# scrape the daily page from the numbers
# https://www.the-numbers.com/box-office-chart/daily/2017/12/15
import datetime as dt

from scrape.scrape_types import ScrapeNumbersDaily
from session import NS
from bs4 import BeautifulSoup, NavigableString
import pathlib, re
from colors import bcolors


def _find_header_index(
    headers: list[str], candidates: list[str], default: int
) -> int:
    for i, header in enumerate(headers):
        for candidate in candidates:
            if candidate in header:
                return i

    return default


def _parse_money_to_int(value: str) -> int | None:
    cleaned = value.strip().replace("$", "").replace(",", "")

    if cleaned in {"", "-", "—"}:
        return None

    if "%" in cleaned:
        return None

    match = re.search(r"-?\d+", cleaned)
    if match is None:
        return None

    return int(match.group(0))


def scrape_movies_daily(soup: BeautifulSoup, date: dt.date) -> list[ScrapeNumbersDaily]:
    """
    Scrape the daily box office page from the numbers
    """
    table_id = "box_office_daily_table"

    table = soup.find("table", id=table_id)

    if table is None:
        table = soup.find("table", class_="chart-desktop")

    if table is None:
        print(
            bcolors.FAIL
            + f"No table found with id={table_id} or class=chart-desktop"
            + bcolors.ENDC
        )
        print(soup.prettify())
        print(bcolors.FAIL + "Skipping scrape" + bcolors.ENDC)
        return []

    tbody = table.find("tbody")

    if tbody is None:
        print(bcolors.WARNING + "No tbody found in table" + bcolors.ENDC)
        return []

    if isinstance(tbody, int):
        print(bcolors.FAIL + "tbody is an int" + bcolors.ENDC)
        return []

    if isinstance(tbody, NavigableString):
        print(bcolors.FAIL + "tbody is a NavigableString" + bcolors.ENDC)
        return []

    rows = tbody.find_all("tr")

    if not rows:
        print(bcolors.WARNING + "No rows found in table" + bcolors.ENDC)
        return []

    header_row = table.find("tr")
    if header_row is None:
        print(bcolors.FAIL + "No header row found in table" + bcolors.ENDC)
        return []

    header_cells = header_row.find_all("th")
    normalized_headers = [
        h.get_text(" ", strip=True).replace("\xa0", " ").lower()
        for h in header_cells
    ]

    title_index = _find_header_index(normalized_headers, ["title"], default=2)
    prev_index = _find_header_index(normalized_headers, ["prev"], default=1)
    gross_index = _find_header_index(
        normalized_headers,
        ["daily gross", "gross"],
        default=4,
    )
    theaters_index = _find_header_index(normalized_headers, ["theaters"], default=7)

    movies: list[ScrapeNumbersDaily] = []

    for row in rows:
        cells = row.find_all("td")

        if len(cells) <= max(title_index, prev_index, gross_index, theaters_index):
            continue

        prev_token = (
            cells[prev_index]
            .get_text(" ", strip=True)
            .replace("(", "")
            .replace(")", "")
            .strip()
            .lower()
        )

        is_new = False
        if prev_token in {"n", "new"}:
            is_new = True

        is_preview = False
        if prev_token in {"p", "preview", "pv"}:
            is_preview = True

        slug_cell = cells[title_index]
        a_tag = slug_cell.find("a")

        if a_tag is None:
            print(bcolors.FAIL + "No a tag found in slug cell" + bcolors.ENDC)
            print(slug_cell)
            print(bcolors.FAIL + "Skipping row" + bcolors.ENDC)
            continue

        href = a_tag["href"]

        title_text = slug_cell.get_text(" ", strip=True).lower()
        if "preview" in title_text:
            is_preview = True

        raw = r"^/movie/([^?#]+)"

        match = re.match(raw, href)

        if match is None:
            print(bcolors.FAIL + f"Could not match href {href} with regex {raw}" + bcolors.ENDC)
            print(bcolors.FAIL + "Skipping row" + bcolors.ENDC)
            continue

        number_slug = match.group(1)

        gross_cell = cells[gross_index]

        is_estimate = False

        # if the gross cell has the estimate class, then it is an estimate
        if "estimate" in (gross_cell.get("class") or []):
            is_estimate = True

        gross_text = gross_cell.get_text(strip=True)
        gross = _parse_money_to_int(gross_text)
        if gross is None:
            continue

        theaters_cell = cells[theaters_index]

        theaters_text = theaters_cell.get_text(strip=True)
        if theaters_text in {"", "-", "—"}:
            theaters = 0
        else:
            replaced = theaters_text.replace(",", "")

            # \xa0
            if "\xa0" in replaced:
                print(
                    bcolors.WARNING
                    + f"Found \\xa0 in theaters cell for {number_slug} on {date}, NONE"
                    + bcolors.ENDC
                )
                theaters = None
            else:
                try:
                    theaters = int(replaced)
                except ValueError:
                    replaced = replaced.replace("(v)", "") # movies can report virtual theaters https://www.the-numbers.com/box-office-chart/daily/2020/04/12
                    theaters = int(replaced)

        movies.append(
            ScrapeNumbersDaily(
                numbers_slug=number_slug,
                date=date,
                revenue=gross,
                theaters=theaters,
                is_new_release=is_new,
                is_preview=is_preview,
                is_estimate=is_estimate,
            )
        )

    return movies


def scrape_numbers_daily(
    date: dt.date, override_html: bool = False
) -> list[ScrapeNumbersDaily]:
    """
    Scrape the daily box office page from the numbers
    """
    html_path = pathlib.Path(
        # 0 pad
        f"boxoffice/html/daily/{date.strftime('%Y')}-{date.strftime('%m')}-{date.strftime('%d')}.html"
    )

    if override_html or not html_path.exists():
        padded_url = f"https://www.the-numbers.com/box-office-chart/daily/{date.year}/{date.strftime('%m')}/{date.strftime('%d')}"
        legacy_url = f"https://www.the-numbers.com/box-office-chart/daily/{date.year}/{date.month}/{date.day}"
        padded_url_slash = f"{padded_url}/"
        legacy_url_slash = f"{legacy_url}/"

        r = None
        attempts: list[tuple[str, int]] = []
        for url in [padded_url, padded_url_slash, legacy_url, legacy_url_slash]:
            print(f"Scraping {url}")
            candidate = NS.get(url)
            attempts.append((url, candidate.status_code))
            if candidate.status_code == 200:
                r = candidate
                break

        if r is None:
            attempt_text = ", ".join([f"{url} -> {status}" for url, status in attempts])
            raise ValueError(
                f"Could not fetch daily page for {date} with known URL patterns ({attempt_text})"
            )

        with open(html_path, "w") as f:
            f.write(r.text)

        daily_text = r.text
    else:
        print(f"Using cached html for {date}")
        with open(html_path) as f:
            r = f.read()

        daily_text = r

    soup = BeautifulSoup(daily_text, "html.parser")

    return scrape_movies_daily(soup, date)
