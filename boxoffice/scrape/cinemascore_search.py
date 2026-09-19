from typing import TypedDict, Optional
from session import S
import requests

# import requests as S
import base64


class CinemascoreResult(TypedDict):
    GRADE: str
    TITLE: str
    YEAR: Optional[str]


def get_cinemascore(title: str, year: int) -> str | None:
    """
    Search for a movie on Cinemascore and return its score.

    Args:
        title (str): The title of the movie.
        year (int): The release year of the movie.

    Returns:
        str | None: The Cinemascore rating if found, otherwise None.
    """
    if title[:3] == "The":
        # Strip "The " from the beginning of the title for better search results
        title = title[4:] + ", The"
    elif title[:2] == "A ":
        # Strip "A " from the beginning of the title for better search results
        title = title[2:] + ", A"

    title = title.lower()

    base64_title = base64.b64encode(title.encode("utf-8")).decode("utf-8")

    url = f"https://webapp.cinemascore.com/guest/search/title/{base64_title}"
    # print(f"Requesting Cinemascore for: {title} ({year}) with URL: {url}")
    r = S.get(url)
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred for title: {title} ({year}) - {e}")
        return None

    try:
        results: list[CinemascoreResult] = r.json()
    except requests.exceptions.JSONDecodeError as e:
        print(f"Failed to decode JSON response for title: {title} ({year}) - {e}")
        return None

    if not results:
        return None

    # Filter results by year
    for result in results:
        if "YEAR" not in result or result["YEAR"] is None:
            return None
        
        if int(result["YEAR"]) == year:
            return result["GRADE"]

    # check if any are + or - 1 year
    for result in results:
        if result["YEAR"] is not None and int(result["YEAR"]) in (year - 1, year + 1):
            return result["GRADE"]

    # If no exact match, return None
    return None


if __name__ == "__main__":
    # Example usage
    title = "The Amateur"
    year = 2025
    score = get_cinemascore(title, year)
    if score:
        print(f"Cinemascore for '{title}' ({year}): {score}")
    else:
        print(f"No Cinemascore found for '{title}' ({year}).")
