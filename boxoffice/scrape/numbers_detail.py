# scrape the detail page from the numbers
# https://the-numbers.com/movie/Wild-Wild-West#tab=summary

from scrape.scrape_types import (
    ScrapeNumbersDetail,
    ScrapeMpaaInfo,
    ScrapeMovieDetails,
    SimpleRelease,
    ScrapeBoxOfficeTotals
)
from session import NS
from bs4 import BeautifulSoup
import pathlib
import re
from colors import bcolors


def get_title(soup: BeautifulSoup) -> tuple[str | None, int]:
    # find the first h1 on the page
    h1 = soup.find("h1")

    if h1 is None:
        print(bcolors.FAIL + "No h1 found on page" + bcolors.ENDC)
        return None, 0

    # Wild Wild West (1999)
    # split the text on the (
    split = h1.text.split(" (")

    if len(split) > 2:
        title = " (".join(split[:-1])
        year = split[-1]
    else:
        title, year = split

    # remove the trailing )
    year = year[:-1]

    # convert the year to an int
    year = int(year)

    return title, year


def get_synopsis(soup: BeautifulSoup) -> str | None:
    synopsis = soup.find("div", id="summary")

    if synopsis is None:
        print(bcolors.FAIL + "No synopsis found" + bcolors.ENDC)
        return ""  # this should maybe return None but not sure.

    # find the first h2
    h2 = synopsis.find("h2")

    if h2 is None:
        print(bcolors.FAIL + "No h2 found in synopsis" + bcolors.ENDC)
        return None

    if isinstance(h2, int):
        print(bcolors.FAIL + "h2 is an int" + bcolors.ENDC)
        return None

    # verify that the h2 says "Synopsis"
    if h2.text != "Synopsis":
        print(bcolors.FAIL + "Synopsis h2 does not say 'Synopsis'" + bcolors.ENDC)
        return None

    # find the next sibling
    next_sibling = h2.find_next_sibling()

    if next_sibling is None:
        print(bcolors.FAIL + "No next sibling found after h2" + bcolors.ENDC)
        return None

    if isinstance(next_sibling, int):
        print(bcolors.FAIL + "next_sibling is a string" + bcolors.ENDC)
        return None

    return next_sibling.text


def get_mpaa_information(mpaa_text: str) -> ScrapeMpaaInfo:
    """<tr><td><b>MPAA&nbsp;Rating:</b></td>
    <td><a href="/market/mpaa-rating/PG-13-(US)">PG-13</a> for action violence, sex references and innuendo</td></tr>
    """
    """<tr><td><b>MPAA&nbsp;Rating:</b></td>
<td><a href="/market/mpaa-rating/R-(US)">R</a> for strong sexual content, graphic nudity, rape, drug use and some language.<br>(Rating bulletin 2865 (cert #55304), 12/18/2024)</td></tr>"""
    mpaa_text = mpaa_text.replace("\n", " ")
    if "(, " in mpaa_text:
        mpaa_text = mpaa_text.replace("(, ", "), ")

    if mpaa_text == "Not Rated":
        return ScrapeMpaaInfo(
            mpaa_rating="NR", mpaa_rating_reason="Not Rated", mpaa_rating_date=None
        )

    if mpaa_text == "G":
        return ScrapeMpaaInfo(
            mpaa_rating="G",
            mpaa_rating_reason="General Audiences",
            mpaa_rating_date=None,
        )

    if mpaa_text == "PG":
        return ScrapeMpaaInfo(
            mpaa_rating="PG",
            mpaa_rating_reason="Parental Guidance Suggested",
            mpaa_rating_date=None,
        )

    if mpaa_text == "PG-13":
        return ScrapeMpaaInfo(
            mpaa_rating="PG-13",
            mpaa_rating_reason="Parents Strongly Cautioned",
            mpaa_rating_date=None,
        )

    if mpaa_text == "R":
        return ScrapeMpaaInfo(
            mpaa_rating="R", mpaa_rating_reason="Restricted", mpaa_rating_date=None
        )

    if mpaa_text == "NC-17":
        return ScrapeMpaaInfo(
            mpaa_rating="NC-17", mpaa_rating_reason="Adults Only", mpaa_rating_date=None
        )

    pattern = r"^(G|PG|PG-13|R|NC-17)(\sfor)?\s(.*)\s*\((Rating bulletin\s*(\d+)\s*\((cert #\d+)\),\s*(\d{1,2}/\d{1,2}/\d{4})\))$"

    match = re.match(pattern, mpaa_text)

    if match is None:
        print(mpaa_text)

        pattern2 = r"^(G|PG|PG-13|R|NC-17)\sfor\s(.*)$"

        match = re.match(pattern2, mpaa_text)

        if match is None:
            rating = ""
            reason = ""
            date = ""
            print(
                bcolors.FAIL + f"Could not match mpaa_text: {mpaa_text}" + bcolors.ENDC
            )
        else:
            rating = match.group(1)
            reason = match.group(2)

            date = None
    else:
        rating = match.group(1)
        reason = match.group(3)
        date = match.group(6)

    if reason is None:
        reason = "No reason given"

    return ScrapeMpaaInfo(
        mpaa_rating=rating, mpaa_rating_reason=reason, mpaa_rating_date=date
    )


def get_domestic_releases(releases_text: str) -> list[SimpleRelease]:
    """November 5th, 2014 (IMAX) by Paramount Pictures
    November 5th, 2014 (Limited) by Paramount Pictures
    November 7th, 2014 (Expands Wide) by Paramount Pictures
    December 6th, 2024 (IMAX) by Paramount Pictures
    August 14th, 2020 (Limited) (Canada)
    """

    # print(releases_text)

    # split the text on the newline
    releases = releases_text.split("\n")

    simple_releases = []

    pattern = r"^(.*)\s*\((.*)\)\s*by\s*(.*)$"  # December 20th, 2024 (Limited) by A24

    for release in releases:
        match = re.match(pattern, release)

        if match is None:
            pattern = r"^(.*)\s*\((.*)\)$"  # December 20th, 2024 (Limited)

            match = re.match(pattern, release)

            if match is None:
                # August 14th, 2020 (Limited) (Canada)
                pattern = r"^(.*)\s*\((.*)\s*\((.*)\)\)$"
                match = re.match(pattern, release)

                if match is None:
                    print(
                        bcolors.FAIL
                        + f"Could not match release: {release}"
                        + bcolors.ENDC
                    )
                    continue

                date = match.group(1)
                release_type = match.group(2)
                release_type += f" ({match.group(3)})"

                simple_releases.append(
                    SimpleRelease(date=date, release_type=release_type)
                )

            date = match.group(1)
            release_type = match.group(2)

            simple_releases.append(SimpleRelease(date=date, release_type=release_type))

            continue

        date = match.group(1)
        release_type = match.group(2)

        simple_releases.append(SimpleRelease(date=date, release_type=release_type))

    return simple_releases


def scrape_movie_details(soup: BeautifulSoup) -> ScrapeMovieDetails | None:
    """<tr><td><b>Source:</b></td><td><a href="/market/source/Original-Screenplay">Original Screenplay</a></td></tr>"""
    """<tr><td><b>Genre:</b></td><td><a href="/market/genre/Drama">Drama</a></td></tr>"""
    """<tr><td><b>Production&nbsp;Method:</b></td><td><a href="/market/production-method/Live-Action">Live Action</a></td></tr>"""
    """<tr><td><b>Creative&nbsp;Type:</b></td><td><a href="/market/creative-type/Historical-Fiction">Historical Fiction</a></td></tr>"""
    # get the Movie Details table
    # find an h2 with the text "Movie Details"
    h2 = soup.find("h2", text="Movie Details")

    if h2 is None:
        print(bcolors.FAIL + "No h2 with text 'Movie Details' found" + bcolors.ENDC)
        return None

    # find the next sibling
    next_sibling = h2.find_next_sibling()

    if next_sibling is None:
        print(bcolors.FAIL + "No next sibling found after h2" + bcolors.ENDC)
        return None

    # next sibling should be a table
    if next_sibling.name != "table":
        print(bcolors.FAIL + "next_sibling is not a table" + bcolors.ENDC)
        return None

    rows = next_sibling.find_all("tr")

    if not rows:
        print(bcolors.WARNING + "No rows found in next sibling table" + bcolors.ENDC)
        return None

    source: str | None = None
    genre: str | None = None
    creative_type: str | None = None
    production_method: str | None = None
    keywords: str | None = None
    mpaa_rating: ScrapeMpaaInfo | None = None
    domestic_releases: list[SimpleRelease] | None = None

    for row in rows:
        # check if the row has a td
        tds = row.find_all("td")

        if not tds:
            continue

        if len(tds) != 2:
            continue

        key = tds[0].text
        for br in tds[1].find_all("br"):
            br.replace_with("\n")
        value = tds[1].text

        normalized_key = key.replace("\xa0", " ").strip()

        if normalized_key == "Source:":
            source = value
        elif normalized_key == "Genre:":
            genre = value
        elif normalized_key == "Creative Type:":
            creative_type = value
        elif normalized_key == "Production Method:":
            production_method = value
        elif normalized_key == "Keywords:":
            keywords = value
        elif normalized_key in {"MPAA Rating:", "MPA Rating:"}:
            mpaa_rating = get_mpaa_information(value)
        elif normalized_key == "Domestic Releases:":
            domestic_releases = get_domestic_releases(value)

    if source is None:
        source = "No data"
        # raise ValueError(f"No source found")

    if genre is None:
        genre = "No data"
        # raise ValueError("No genre found")

    if creative_type is None:
        creative_type = "No data"
        # raise ValueError("No creative_type found")

    if production_method is None:
        production_method = "No data"
        # raise ValueError("No production_method found")

    # if keywords is None: # keywords may not exist
    # raise ValueError("No keywords found")

    if mpaa_rating is None:
        mpaa_rating = ScrapeMpaaInfo(
            mpaa_rating="NR",
            mpaa_rating_reason="Not Rated",
            mpaa_rating_date=None,
        )
        # raise ValueError("No MPAA rating found")

    if domestic_releases is None:
        raise ValueError("No domestic releases found")

    # split the keywords on the comma
    if keywords is not None:
        keywords_split = keywords.split(", ")
    else:
        keywords_split = None

    return ScrapeMovieDetails(
        source=source,
        genre=genre,
        creative_type=creative_type,
        production_method=production_method,
        keywords=keywords_split,
        mpaa=mpaa_rating,
        domestic_releases=domestic_releases,
    )


def scrape_box_office_totals(soup: BeautifulSoup) -> ScrapeBoxOfficeTotals | None:
    """<table id="movie_finances">
    <tbody><tr class="heading">
    <td colspan="3"><b>Theatrical Performance</b></td>
    </tr>
    <tr>
    <!--    <td><div class="hidden-xs"><b>Domestic Box Office</b></div><div class="visible-xs"><b>Domestic</b></div></td>-->
        <td><b>Domestic Box Office</b></td>
    <td class="data">$197,123,387</td><td><a href="#tab=box-office">Details</a></td>
    </tr>
    <tr>
    <td><b>International Box Office</b></td>
    <td class="data sum">$170,284,359</td><td><a href="#tab=international">Details</a></td>
    </tr>
    <tr>
    <td><b>Worldwide Box Office</b></td>
    <td class="data">$367,407,746</td><td></td>
    </tr>
            <tr class="heading">
                <td colspan="3" class="headed">
                    <style>
    /* Popup container - can be anything you want */
    .popup {
      position: relative;
      display: inline-block;
      cursor: pointer;
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
    }

    /* The actual popup */
    .popup .popuptext {
      /*visibility: hidden;*/
      opacity: 0;
      width: 160px;
      background-color: #555;
      color: #fff;
      text-align: center;
      border-radius: 6px;
      padding: 8px 0;
      position: absolute;
      z-index: 1;
      bottom: 125%;
      left: 50%;
      margin-left: -80px;
    }

    /* Popup arrow */
    .popup .popuptext::after {
      content: "";
      position: absolute;
      top: 100%;
      left: 50%;
      margin-left: -5px;
      border-width: 5px;
      border-style: solid;
      border-color: #555 transparent transparent transparent;
    }

    /* Toggle this class - hide and show the popup */
    .popup .show {
      /*visibility: visible;*/
      -webkit-animation: fadeIn 1s;
      animation: fadeIn 1s;
    }

    /* Add animation (fade in the popup) */
    @-webkit-keyframes fadeIn {
      from {opacity: 0;}
      to {opacity: 1;}
    }

    @keyframes fadeIn {
      from {opacity: 0;}
      to {opacity:1 ;}
    }

    .popup .hide {
      /*visibility: hidden;*/
      -webkit-animation: fadeOut 3s;
      animation: fadeOut 5s;
    }

    /* Add animation (fade in the popup) */
    @-webkit-keyframes fadeOut {
      from {opacity: 1;}
      to {opacity: 0;}
    }

    @keyframes fadeOut {
      from {opacity: 1;}
      to {opacity:0 ;}
    }

    </style>

                      <!-- Hidden text to be copied -->
    <span id="OpusData-link" style="cursor: pointer; color: blue;">
        OpusData ID: 502350100</span>
      <!-- Hidden text to be copied -->
      <span id="textToCopy" class="hidden-text" style="display:none">502350100</span>
       <!-- Copy Icon -->
      <button class="copy-button popup" onclick="copyToClipboard()" title="Copy OpusData ID to clipboard" style="border: none;">
        <i class="fa-regular fa-copy"></i>
        <span class="popuptext" id="copyPopup">Copied OpusData ID: 502350100</span>
      </button>

                      <script>
        function copyToClipboard() {
          const text = document.getElementById("textToCopy").textContent;

          // Create temporary textarea to copy from
          const textarea = document.createElement("textarea");
          textarea.value = text;
          document.body.appendChild(textarea);
          textarea.select();
          document.execCommand("copy");
          document.body.removeChild(textarea);
    var popup = document.getElementById("copyPopup");
      //popup.classList.toggle("show");
      popup.classList.toggle("hide");

        }
      </script>

                </td>
            </tr>

                 <script>
      const part1 = 'https://www.opusdata.com/';
      const part2 = 'movie/502350100';

      href = part1 + part2;

      document.getElementById('OpusData-link').addEventListener('click', () => {
             window.location.href = href;
      });

      document.body.appendChild(a);
    </script>



    <tr class="heading"><td colspan="3" class="headed"><a href="#more" class=" inactive">Further financial details...</a></td></tr>
    </tbody></table>"""

    # find the table with id movie_finances
    table = soup.find("table", id="movie_finances")

    if table is None:
        print(bcolors.FAIL + "No table with id 'movie_finances' found" + bcolors.ENDC)
        return None

    # find all the rows in the table
    rows = table.find_all("tr")

    domestic_total = 0
    international_total = 0
    worldwide_total = 0

    for row in rows:
        # check if the row has a td
        tds = row.find_all("td")

        if not tds or len(tds) < 2:
            continue

        key = tds[0].text.strip()
        value_text = tds[1].text.strip()

        # remove the dollar sign and commas from the value
        value_text = value_text.replace("$", "").replace(",", "")

        try:
            value = int(value_text)
        except ValueError:
            print(bcolors.FAIL + f"Could not convert {value_text} to int" + bcolors.ENDC)
            continue

        if key == "Domestic Box Office":
            domestic_total = value
        elif key == "International Box Office":
            international_total = value
        elif key == "Worldwide Box Office":
            worldwide_total = value

    if domestic_total == 0 and international_total == 0 and worldwide_total == 0:
        print(bcolors.FAIL + "No box office totals found" + bcolors.ENDC)
        return None

    return ScrapeBoxOfficeTotals(
        domestic_total=domestic_total,
        international_total=international_total,
        worldwide_total=worldwide_total,
    )

def scrape_numbers_detail(numbers_slug: str) -> ScrapeNumbersDetail | None:
    # first check if we have the html file saved
    html_path = pathlib.Path(f"boxoffice/html/detail/{numbers_slug}.html")

    url = f"https://the-numbers.com/movie/{numbers_slug}?public=true#tab=summary"

    def scrape_numbers():
        r = NS.get(url)

        r.raise_for_status()

        # write the html to boxoffice/html/detail
        with open(html_path, "w") as f:
            f.write(r.text)

        detail_text = r.text
        return detail_text

    if not html_path.exists():
        detail_text = scrape_numbers()
    else:
        with open(html_path) as f:
            r = f.read()

        if 'Direct access to this page is temporarily restricted' in r:
            print(bcolors.WARNING + f"Direct access to {numbers_slug} is restricted, scraping again." + bcolors.ENDC)
            detail_text = scrape_numbers()

        detail_text = r

    soup = BeautifulSoup(detail_text, "html.parser")

    synopsis = get_synopsis(soup)
    title, release_year = get_title(soup)
    movie_details = scrape_movie_details(soup)

    if title is None or movie_details is None:
        # print the page
        print(bcolors.FAIL + f"Could not scrape title or movie details from url {url}" + bcolors.ENDC)
        print(soup.prettify())
        return None
    
    box_office_totals = scrape_box_office_totals(soup)

    return ScrapeNumbersDetail(
        numbers_slug=numbers_slug,
        numbers_title=title,
        release_year=release_year,
        numbers_synopsis=synopsis,
        mpaa_rating=movie_details.mpaa.mpaa_rating,
        mpaa_rating_date=movie_details.mpaa.mpaa_rating_date,
        mpaa_rating_reason=movie_details.mpaa.mpaa_rating_reason,
        source=movie_details.source,
        genre=movie_details.genre,
        creative_type=movie_details.creative_type,
        production_method=movie_details.production_method,
        keywords=movie_details.keywords,
        domestic_releases=movie_details.domestic_releases,
        domestic_gross=box_office_totals.domestic_total if box_office_totals else 0,
        international_gross=box_office_totals.international_total if box_office_totals else 0,
        worldwide_gross=box_office_totals.worldwide_total if box_office_totals else 0,
    )
