from scrape.scrape_types import ScrapeBoxOfficeTotals
from session import S
from bs4 import BeautifulSoup

# If Numbers keeps being bad, scrape the worldwide totals from Box Office Mojo
# Potentially start scraping a lot of stuff from Box Office Mojo

def scrape_box_office_mojo_totals(imdb_id: str) -> ScrapeBoxOfficeTotals:
    r = S.get(f'https://www.boxofficemojo.com/title/tt{imdb_id}/')

    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'html.parser')

    body = soup.find('body')
    if not body:
        raise ValueError('No body found in Box Office Mojo page')
    
    # Find div with class 'mojo-performance-summary-table'
    summary_table = body.find('div', class_='mojo-performance-summary-table')
    if not summary_table:
        raise ValueError('No summary table found in Box Office Mojo page')
    
    """<div class="a-section a-spacing-none mojo-performance-summary-table">
            <h2 class="a-size-large a-text-bold">
                All Releases
            </h2>
                <div class="a-section a-spacing-none">
                    <span class="a-size-small">
                                Domestic (<span class="percent">58.7%</span>)
                    </span>
                    <br>
                    <span class="a-size-medium a-text-bold">
                                <span class="money">$21,417,396</span>
                    </span>
                </div>
                <div class="a-section a-spacing-none">
                    <span class="a-size-small">
                                International (<span class="percent">41.3%</span>)
                    </span>
                    <br>
                    <span class="a-size-medium a-text-bold">
                                <span class="money">$15,075,098</span>
                    </span>
                </div>
                <div class="a-section a-spacing-none">
                    <span class="a-size-small">
                                Worldwide 
                    </span>
                    <br>
                    <span class="a-size-medium a-text-bold">
                                <span class="money">$36,492,494</span>
                    </span>
                </div>
</div>"""
    monies = summary_table.find_all('span', class_='a-size-medium a-text-bold')

    if len(monies) < 3:
        raise ValueError('Not enough money spans found in Box Office Mojo page')

    domestic = monies[0].text.strip()
    international = monies[1].text.strip()
    worldwide = monies[2].text.strip()

    domestic = int(domestic.replace('$', '').replace(',', '')) if domestic != '–' else 0
    international = int(international.replace('$', '').replace(',', '')) if international != '–' else 0
    worldwide = int(worldwide.replace('$', '').replace(',', '')) if worldwide != '–' else 0

    return ScrapeBoxOfficeTotals(
        domestic_total=domestic,
        international_total=international,
        worldwide_total=worldwide
    )


