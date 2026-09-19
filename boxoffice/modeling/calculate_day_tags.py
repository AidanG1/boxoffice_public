import datetime as dt
from enum import Enum
from database.types import SumByDayRPC
from database.db import supabase
import numpy as np
from pydantic import BaseModel

class YearDayTag(Enum):
    """https://www.usa.gov/holidays this list plus some"""

    # once a year
    april_fools_day = 0
    new_years_day = 1
    mlk_day = 2
    valentines_day = 3
    presidents_day = 4
    super_bowl_sunday = 5
    super_bowl_saturday = 6
    memorial_day = 7
    juneteenth = 8
    independence_day = 9
    labor_day = 10
    columbus_day = 11
    veterans_day = 12
    thanksgiving_day = 13
    black_friday = 14
    christmas_day = 15
    oscars_day = 16
    mothers_day = 17
    fathers_day = 18
    halloween = 19
    christmas_eve = 20
    new_years_eve = 21
    easter_sunday = 22
    inauguration_day = 23
    election_day = 24
    feb_13 = 25
    feb_15 = 26
    dec_26 = 27
    dec_27 = 28
    dec_28 = 29
    dec_29 = 30
    thanksgiving_saturday = 31
    thanksgiving_sunday = 32
    easter_monday = 33

type DayTagsDict = dict[dt.date, list[YearDayTag]]

class DayTagsData(BaseModel):
    day_tags_dict: DayTagsDict
    tag_weight_averages: list[float]
    days_since_first_friday_weight_averages: list[float]

DAY_TAG_FILENAME = "boxoffice/modeling/day_tags.json"
start_date = dt.date(2015, 1, 1)
end_date = dt.date(2025, 1, 1)

def get_days_since_first_friday(date: dt.date) -> int:
    # make sure that date is a date and not a datetime
    date = dt.date(date.year, date.month, date.day)
    first_friday = dt.date(date.year, 1, 1)
    while first_friday.weekday() != 4:
        first_friday += dt.timedelta(days=1)

    return (date - first_friday).days


days_since_first_friday_weights: list[list[float] | None] = [None] * (
    366 + 6
)  # previous sum and count
tag_weights: list[list[float] | None] = [None] * len(
    YearDayTag
)  # previous sum and count


def create_day_tags() -> DayTagsDict:
    # make day tags for every day from January 1st, 2015 to December 31st, 2026
    super_bowl_dates = [
        dt.date(2015, 2, 1),
        dt.date(2016, 2, 7),
        dt.date(2017, 2, 5),
        dt.date(2018, 2, 4),
        dt.date(2019, 2, 3),
        dt.date(2020, 2, 2),
        dt.date(2021, 2, 7),
        dt.date(2022, 2, 13),
        dt.date(2023, 2, 12),
        dt.date(2024, 2, 11),
        dt.date(2025, 2, 9),
        dt.date(2026, 2, 8),
    ]

    oscars_dates = [
        dt.date(2015, 2, 22),
        dt.date(2016, 2, 28),
        dt.date(2017, 2, 26),
        dt.date(2018, 3, 4),
        dt.date(2019, 2, 24),
        dt.date(2020, 2, 9),
        dt.date(2021, 4, 25),
        dt.date(2022, 3, 27),
        dt.date(2023, 3, 12),
        dt.date(2024, 3, 10),
        dt.date(2025, 3, 2),
        dt.date(2026, 3, 8),
    ]

    easter_dates = [
        dt.date(2015, 4, 5),
        dt.date(2016, 3, 27),
        dt.date(2017, 4, 16),
        dt.date(2018, 4, 1),
        dt.date(2019, 4, 21),
        dt.date(2020, 4, 12),
        dt.date(2021, 4, 4),
        dt.date(2022, 4, 17),
        dt.date(2023, 4, 9),
        dt.date(2024, 3, 31),
        dt.date(2025, 4, 20),
        dt.date(2026, 4, 5),
    ]
    day_tags: DayTagsDict = {}

    for year in range(2015, 2027):
        for month in range(1, 13):
            for day in range(1, 32):
                try:
                    date = dt.date(year, month, day)
                except ValueError:
                    continue

                day_tags[date] = []

                if date.month == 1:
                    if date.day == 1:
                        day_tags[date].append(YearDayTag.new_years_day)
                    if date.weekday() == 0 and date.day > 14 and date.day < 21:
                        day_tags[date].append(YearDayTag.mlk_day)

                if date.month == 2:
                    if date.day == 14:
                        day_tags[date].append(YearDayTag.valentines_day)
                    # if date.day == 13:
                    #     day_tags[date].append(YearDayTag.feb_13)
                    # if date.day == 15:
                    #     day_tags[date].append(YearDayTag.feb_15)
                    if date.weekday() == 0 and date.day > 14 and date.day < 21:
                        day_tags[date].append(YearDayTag.presidents_day)

                if date.month == 4:
                    if date.day == 1:
                        day_tags[date].append(YearDayTag.april_fools_day)

                if date.month == 5:
                    if date.weekday() == 0 and date.day > 24 and date.day < 31:
                        day_tags[date].append(YearDayTag.memorial_day)
                    if date.weekday() == 6 and date.day > 10 and date.day < 16:
                        day_tags[date].append(YearDayTag.mothers_day)

                if date.month == 6:
                    # if date.day == 19:
                    #     day_tags[date].append(YearDayTag.juneteenth)
                    if date.weekday() == 6 and date.day > 14 and date.day < 21:
                        day_tags[date].append(YearDayTag.fathers_day)

                if date.month == 7 and date.day == 4:
                    day_tags[date].append(YearDayTag.independence_day)
                if date.month == 9 and date.weekday() == 0 and date.day > 7 and date.day < 14:
                    day_tags[date].append(YearDayTag.labor_day)
                if date.month == 10:
                    if date.weekday() == 0 and date.day > 7 and date.day < 15:
                        day_tags[date].append(YearDayTag.columbus_day)
                    if date.day == 31:
                        day_tags[date].append(YearDayTag.halloween)

                if date.month == 11:
                    if date.day == 11:
                        day_tags[date].append(YearDayTag.veterans_day)
                    if date.weekday() == 3 and date.day > 21 and date.day < 29:
                        day_tags[date].append(YearDayTag.thanksgiving_day)
                    if date.weekday() == 4 and date.day > 22 and date.day < 30:
                        day_tags[date].append(YearDayTag.black_friday)
                    if date.weekday() == 5 and date.day > 23 and date.day < 31:
                        day_tags[date].append(YearDayTag.thanksgiving_saturday)
                    if date.weekday() == 6 and date.day > 24 and date.day < 32:
                        day_tags[date].append(YearDayTag.thanksgiving_sunday)

                if date.month == 12:
                    if date.weekday() == 5 and date.day == 1:
                        day_tags[date].append(YearDayTag.thanksgiving_saturday)
                    if date.weekday() == 6 and date.day <= 2:
                        day_tags[date].append(YearDayTag.thanksgiving_sunday)
                    # if date.day == 24:
                    #     day_tags[date].append(YearDayTag.christmas_eve)
                    if date.day == 31:
                        day_tags[date].append(YearDayTag.new_years_eve)
                    # if date.day == 25:
                    #     day_tags[date].append(YearDayTag.christmas_day)
                    # if date.day == 26:
                    #     day_tags[date].append(YearDayTag.dec_26)
                    # if date.day == 27:
                    #     day_tags[date].append(YearDayTag.dec_27)
                    # if date.day == 28:
                    #     day_tags[date].append(YearDayTag.dec_28)
                    # if date.day == 29:
                    #     day_tags[date].append(YearDayTag.dec_29)

                # if date == oscars_dates[year - 2015]:
                #     day_tags[date].append(YearDayTag.oscars_day)
                if date == super_bowl_dates[year - 2015]:
                    day_tags[date].append(YearDayTag.super_bowl_sunday)
                if date == super_bowl_dates[year - 2015] - dt.timedelta(days=1):
                    day_tags[date].append(YearDayTag.super_bowl_saturday)
                if date == easter_dates[year - 2015]:
                    day_tags[date].append(YearDayTag.easter_sunday)
                if date == easter_dates[year - 2015] + dt.timedelta(days=1):
                    day_tags[date].append(YearDayTag.easter_monday)

                if year % 4 == 0:
                    if date.month == 1 and date.day == 20:
                        day_tags[date].append(YearDayTag.inauguration_day)

                if year % 4 == 3:
                    if (
                        date.month == 11
                        and date.weekday() == 1
                        and date.day > 2
                        and date.day < 8
                    ):
                        day_tags[date].append(YearDayTag.election_day)

    return day_tags


def get_day_tags(date: dt.date, day_tags: DayTagsDict) -> list[YearDayTag]:
    return day_tags[date]


##################
# Get the data from the database
##################

def get_sum_data(
    start_date: dt.date, end_date: dt.date
) -> list[SumByDayRPC]:
    """Get the data from the database"""
    sum_by_day_data: list[SumByDayRPC] = (
        supabase.rpc(
            "sum_by_day",
            {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "filter_x_days": 0,
            },
        )
        .execute()
        .data
    )
    return sum_by_day_data


################
# Get the first Friday of each year
################
def get_first_fridays_dict(
    start_date: dt.date, end_date: dt.date
) -> dict[int, int]:
    first_fridays_in_year: dict[int, int] = {}
    for i in range(start_date.year, end_date.year + 1):
        date = dt.date(i, 1, 1)
        while date.weekday() != 4:
            date += dt.timedelta(days=1)
        first_fridays_in_year[i] = date.timetuple().tm_yday
    return first_fridays_in_year

##############
# Get the total box office and budget for the entire data set
##############
def get_total_box_office_and_budget(
    sum_by_day_data: list[SumByDayRPC]
) -> tuple[float, float]:
    all_box_office_sum = 0
    all_weighted_budget_sum = 0
    for day in sum_by_day_data:
        all_box_office_sum += day["revenue"]
        all_weighted_budget_sum += day["theater_weighted_budget"]
    return all_box_office_sum, all_weighted_budget_sum

##################
# Calculate the median day of week ratios
##################

def calculate_median_day_of_week_ratios(
    sum_by_day_data: list[SumByDayRPC],
    start_date: dt.date,
) -> list[list[tuple[float, float]] | None]:
    # get the median multiplier for each day of the week over the course of the year
    # for each day of the week, get the ratio of revenue to budget
    # for each day of the week, get the median ratio
    # for each day of the week, get the median ratio for each day of the week over the course of the year
    # and then divide by that
    # for all of these, get the median multiplier for each day of the week over the course of the year and then divide by that
    median_day_of_week_ratios: list[list[tuple[float, float]] | None] = [
        None for _ in range(7)
    ]
    for i, day in enumerate(sum_by_day_data[1:], 1):
        date = dt.datetime.strptime(day["date"], "%Y-%m-%d").date()
        days_ago = (date - start_date).days
        if day["revenue"] < 100000:
            # skip the bad covid days
            continue
        ratio = day["revenue"] / day["theater_weighted_budget"]

        weekday = date.weekday()
        median_weekday = median_day_of_week_ratios[weekday]
        if median_weekday is None:
            median_day_of_week_ratios[weekday] = [(ratio, days_ago)]
        else:
            median_weekday.append((ratio, days_ago))

    return median_day_of_week_ratios

def weighted_median(pairs: list[tuple[float, float]]) -> float:
    values, weights = zip(*pairs)
    i = np.argsort(values)
    c = np.cumsum(weights)
    return values[i[np.searchsorted(c, 0.5 * c[-1])]]

def calculate_day_tags() -> DayTagsData:
    day_tags = create_day_tags()
    sum_by_day_data = get_sum_data(start_date, end_date)
    median_day_of_week_ratios = calculate_median_day_of_week_ratios(
        sum_by_day_data, start_date
    )
    first_fridays_in_year = get_first_fridays_dict(start_date, end_date)

    weighted_median_ratios: list[float] = [weighted_median(values) for values in median_day_of_week_ratios]

    for i, value in enumerate(weighted_median_ratios):
        if value is not None:
            print(f"End day {i} median adjusted gross: {value}")

    ##################
    # Calculating median day of week ratios done
    ##################


    for day in sum_by_day_data:
        date = dt.datetime.strptime(day["date"], "%Y-%m-%d").date()
        weekday = date.weekday()
        weekday_median = weighted_median_ratios[weekday]

        if day["revenue"] < 100000:
            # skip the bad covid days
            continue

        # print(day)
        adjusted_value = day["revenue"] / day["theater_weighted_budget"] / weekday_median

        tags = get_day_tags(date, day_tags)
        if len(tags) > 0:
            for tag in tags:
                tag_weights_value = tag_weights[tag.value]
                if tag_weights_value is None:
                    tag_weights[tag.value] = [adjusted_value]
                else:
                    tag_weights_value.append(adjusted_value)
        else:
            day_of_year = date.timetuple().tm_yday

            days_since_first_friday = day_of_year - first_fridays_in_year[date.year]

            days_since_first_friday_value = days_since_first_friday_weights[
                days_since_first_friday
            ]
            if days_since_first_friday_value is None:
                days_since_first_friday_weights[days_since_first_friday] = [adjusted_value]
            else:
                days_since_first_friday_value.append(adjusted_value)

    tag_weight_averages: list[float] = [0 for _ in tag_weights]

    days_since_first_friday_weight_averages: list[float] = [
        0 for _ in days_since_first_friday_weights
    ]
    for i, values in enumerate(days_since_first_friday_weights):
        ratios = median_day_of_week_ratios[(i + 4) % 7]
        if values is not None and ratios is not None:
            days_since_first_friday_weight_averages[i] = (
                float(
                    np.median(values)
                )
                # * (
                #     all_weighted_budget_sum / all_box_office_sum
                # )  ** 2 # this is a uniform adjustment to make the average around 1
            )

    # for every weight multiply by all box office sum and divide by all weighted budget sum
    for i, values in enumerate(tag_weights):
        if values is not None:
            tag_weight_averages[i] = float(
                np.median(values)
            )

    return DayTagsData(
        day_tags_dict=day_tags,
        tag_weight_averages=tag_weight_averages,
        days_since_first_friday_weight_averages=days_since_first_friday_weight_averages,
    )

    # print(f"{tag_weight_averages=}")
    # print(f"{days_since_first_friday_weight_averages=}")

def get_day_tag_data() -> DayTagsData:
    """
    check if the file exists and if so, load it
    if not, create it and save it
    """
    from dotenv import load_dotenv

    load_dotenv()

    import os

    base_dir = os.getenv("BASE_DIR")

    filename = os.path.join(base_dir, DAY_TAG_FILENAME)

    try:
        with open(filename, "r") as f:
            data = f.read()
            return DayTagsData.model_validate_json(data)
    except FileNotFoundError:
        print("File not found, creating day tags")
        day_tags_data = calculate_day_tags()
        with open(filename, "w") as f:
            f.write(day_tags_data.model_dump_json())
        return day_tags_data