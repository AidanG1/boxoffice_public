# https://www.hsx.com/search/?keyword=interstellar&status=ALL&type=1&minprice=min&maxprice=max&release=&phase_id=&genre_id=&distributor_id=&action=submit_advanced

# https://www.hsx.com/security/view/PADT3

from scrape.scrape_types import HSX
from session import S
from bs4 import BeautifulSoup
from colors import bcolors


def scrape_hsx_for_id(ticker: str) -> int | None:
    url = f"https://www.hsx.com/security/view/{ticker}"
    r = S.get(url)
    r.raise_for_status()

    text = r.text

    # id="pricehistory-42684"
    # find the string pricehistory-
    index = text.find("pricehistory-")

    if index == -1:
        return None

    # get the id which is the next numbers until not a digit
    id_start = index + len("pricehistory-")
    id_end = id_start

    while text[id_end].isdigit():
        id_end += 1

    return int(text[id_start:id_end])


def search_hsx_ticker(title: str) -> HSX | None:
    # lol hsx search sucks so replace apostrophes with underscores
    title = title.replace("'", "_")
    
    url = f"https://www.hsx.com/search/?keyword={title}&status=ALL&type=1&minprice=min&maxprice=max&release=&phase_id=&genre_id=&distributor_id=&action=submit_advanced"
    r = S.get(url)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # find a table with the class sortable
    table = soup.find("table", class_="sortable")

    if table is None:
        print(bcolors.FAIL + f"HSX Ticker Error: No table found on page {url}" + bcolors.ENDC)
        return None

    tbody = table.find("tbody")

    if tbody is None:
        print(bcolors.FAIL + f"HSX Ticker Error: No tbody found in table" + bcolors.ENDC)
        return None

    if isinstance(tbody, int):
        print(bcolors.FAIL + f"HSX Ticker Error: tbody is not a tag" + bcolors.ENDC)
        return None

    rows = tbody.find_all("tr")

    if not rows:
        print(bcolors.FAIL + f"HSX Ticker Error: No rows found in table" + bcolors.ENDC)
        return None

    # get the first row
    row = rows[0]

    # get the second column
    second_column_tds = row.find_all("td")

    if len(second_column_tds) < 2:
        print(bcolors.FAIL + f"HSX Ticker Error: Not enough columns in row" + bcolors.ENDC)
        return None

    second_column = row.find_all("td")[1]

    # get the text from the second column
    ticker = second_column.text

    id = scrape_hsx_for_id(ticker)

    return HSX(hsx_ticker=ticker, hsx_id=id)
