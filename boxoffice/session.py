import requests, os
from dotenv import load_dotenv
import cloudscraper

load_dotenv()

fake_browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

S = requests.Session()
"""Requests session for general"""

S.headers = {"User-Agent": fake_browser_ua}

NS = requests.Session()  # for numbers
"""Requests session for Numbers API"""

NS.headers = {"User-Agent": fake_browser_ua, "Referer": "https://www.the-numbers.com/daily-box-office-chart"}

WS = requests.Session()  # for wikipedia
"""Requests session for Wikipedia"""

WS.headers = {"User-Agent": "Statistical Machine Learning Box Office Scraper"}

TS = requests.Session()  # for tmdb
"""Requests session for TMdB API"""

TS.headers = {
    "User-Agent": "Statistical Machine Learning Box Office Scraper",
    "Authorization": f"Bearer {os.getenv('TMDB_KEY')}",
}

scraper = cloudscraper.create_scraper()

scraper.headers.update({"User-Agent": fake_browser_ua})
