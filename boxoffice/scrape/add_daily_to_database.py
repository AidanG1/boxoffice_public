from scrape.db_wrapper import db_wrapper
from scrape.scrape_types import ScrapeNumbersDaily, BoxOfficeDayToInsert


def add_daily_to_database(numbers_daily: list[ScrapeNumbersDaily]) -> None:
    """
    Add the daily numbers to the database
    """
    box_office_days: list[BoxOfficeDayToInsert] = []

    for daily in numbers_daily:
        # get the movie id
        movie_id = db_wrapper.get_movie_id(daily.numbers_slug)

        if movie_id is None:
            raise ValueError(f"Could not find movie {daily.numbers_slug}")

        box_office_days.append(
            BoxOfficeDayToInsert(
                movie_id=movie_id,
                date=daily.date,
                revenue=daily.revenue,
                theaters=daily.theaters,
                is_preview=daily.is_preview,
                is_new_release=daily.is_new_release,
                is_estimate=daily.is_estimate,
            )
        )

    db_wrapper.bulk_create_box_office_days(box_office_days)
