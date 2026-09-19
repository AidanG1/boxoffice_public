from collections import defaultdict
from colors import bcolors
from copy import deepcopy
from database.db import supabase
from database.types import KNNRPC, Boxofficeday, Movie, MovieInfoDay, MovieReleaseDate
from dotenv import load_dotenv
from httpx import ReadError, RemoteProtocolError
from io import BytesIO
from matplotlib.axes import Axes
from modeling.day_tags import get_adjustment_weight
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mplcursors import cursor
from PIL import Image
from pydantic import BaseModel
from session import S
from typing import TypedDict
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pickle
import seaborn as sns
import statsmodels.api as sm
import time

load_dotenv()


class MoviePredictions(BaseModel):
    existing: list[int]
    predicted: list[int]
    actual: list[int]
    movie: Movie
    start_predictions_date: dt.date


class PredictionMetrics(BaseModel):
    mape: float
    rmse: float
    mapd: float
    wmapd: float
    sae: float
    wmapd_by_index: float


class MovieCache(TypedDict):
    movie: Movie
    boxofficedays: list[Boxofficeday]  # this one is adjusted
    original_boxofficedays: list[Boxofficeday]  # do not adjust this one
    movie_info_days: list[MovieInfoDay]
    release_dates: list[MovieReleaseDate]
    budget: int


# {"mpaa_rating": 1, "source": 1, "genre": 1, "production_method": 1, "creative_type": 1, "budget": 1, "genres": 1, "spoken_languages": 1, "production_countries": 0.5, "production_companies": 0.5, "release_dates": 4, "release_dates_count": 3}
class KNNWeights(TypedDict):
    mpaa_rating: float
    source: float
    genre: float
    production_method: float
    creative_type: float
    budget: float
    genres: float
    spoken_languages: float
    production_countries: float
    production_companies: float
    release_dates: float
    release_dates_count: float


def default_knn_weights() -> KNNWeights:
    return KNNWeights(
        mpaa_rating=1.22,
        source=1.32,
        genre=1.08,
        production_method=1.66,
        creative_type=0.52,
        budget=0.77,
        genres=0.86,
        spoken_languages=1.42,
        production_countries=0.31,
        production_companies=0.62,
        release_dates=3.18,
        release_dates_count=2.08,
    )

    return KNNWeights(
        mpaa_rating=1,
        source=1,
        genre=1,
        production_method=1,
        creative_type=1,
        budget=1,
        genres=1,
        spoken_languages=1,
        production_countries=0.5,
        production_companies=0.5,
        release_dates=4,
        release_dates_count=3,
    )


def default_k() -> int:
    return 8
    return 10


# create caches
movie_id_to_cache: dict[str, MovieCache] = {}


class TitleBudget(TypedDict):
    title: str
    budget: int


class Multiplier(TypedDict):
    end_weekday: int
    multiplier: float
    weight: float
    end_days_after_first_friday: int
    release_type: str
    theater_count_multiplier: float


class BetweenReleaseTypeMultiplier(TypedDict):
    multiplier: float
    start_theater_count: int
    end_theater_count: int
    start_release_type: str
    end_release_type: str
    end_days_after_first_friday: int


class ActualPredicted(TypedDict):
    actual: int
    predicted: int


def predict_opening_day(movie: MovieCache, opening_date: dt.date) -> int:
    """
    This returns an adjusted value
    """
    with open("boxoffice/opening_day_model.pkl", "rb") as f:
        model = pickle.load(f)

    pre_release_cumulative_wikipedia_views = 0

    for day in movie["movie_info_days"]:
        if dt.datetime.strptime(day["date"], "%Y-%m-%d").date() > opening_date:
            break
        if day["wikipedia_views"] is None:
            continue
        pre_release_cumulative_wikipedia_views += day["wikipedia_views"]

    # get the in_franchise value
    if movie["movie"] is None:
        raise ValueError("Movie not found, is None")
    if movie["movie"]["collection_id"] is not None:
        in_franchise = 1
    else:
        in_franchise = 0
    # get the budget
    if movie["budget"] is None:
        budget = 0
    else:
        budget = movie["budget"]

    df = pd.DataFrame(
        {
            "budget": [budget],
            "pre_release_cumulative_wikipedia_views": [
                pre_release_cumulative_wikipedia_views
            ],
            "in_franchise": [in_franchise],
        }
    )

    # run the model
    prediction = model.predict(df)[0]

    # adjust the prediction
    adjustment = get_adjustment_weight(opening_date)

    prediction = int(prediction / adjustment)

    # return the prediction
    return prediction


def predict_opening_day_by_movie_id_using_knn(
    movie_id: str,
) -> ActualPredicted:
    movie_cache = get_single_movie_data(movie_id)
    if movie_cache is None:
        raise ValueError(f"Movie with id {movie_id} not found")
    knn_caches = get_knn_data(movie_id)

    return predict_opening_day_by_knn(movie_cache, list(knn_caches.values()))


def predict_opening_day_by_knn(
    movie: MovieCache, knn: list[MovieCache]
) -> ActualPredicted:
    """
    Trains an MLR on the KNN and predicts the opening day revenue for the movie
    This returns an adjusted value, need to get the date to return the unadjusted value later
    """

    formula = "opening_day ~ 0 + budget + pre_release_cumulative_wikipedia_views + youtube_sum_all_views"

    knn_dict = {
        "budget": [],
        "pre_release_cumulative_wikipedia_views": [],
        "youtube_sum_all_views": [],
        "opening_day": [],
    }

    for x in knn:
        first_date = dt.datetime.strptime(
            x["boxofficedays"][0]["date"], "%Y-%m-%d"
        ).date()

        wiki_views = 0
        for day in x["movie_info_days"]:
            if dt.datetime.strptime(day["date"], "%Y-%m-%d").date() > first_date:
                break
            if day["wikipedia_views"] is None:
                continue
            wiki_views += day["wikipedia_views"]

        youtube_views = 0
        for day in x["movie_info_days"]:
            if dt.datetime.strptime(day["date"], "%Y-%m-%d").date() > first_date:
                break
            if day["youtube_sum_all_views"] is None:
                continue
            youtube_views = day["youtube_sum_all_views"]
        knn_dict["opening_day"].append(x["boxofficedays"][0]["revenue"])
        knn_dict["budget"].append(x["budget"])
        knn_dict["pre_release_cumulative_wikipedia_views"].append(wiki_views)
        knn_dict["youtube_sum_all_views"].append(youtube_views)

    knn_df = pd.DataFrame(knn_dict)

    model = sm.RLM.from_formula(
        formula,
        data=knn_df,
    ).fit()

    test_dict = {
        "budget": movie["budget"],
        "pre_release_cumulative_wikipedia_views": 0,
        "youtube_sum_all_views": 0,
    }

    first_date = dt.datetime.strptime(
        movie["boxofficedays"][0]["date"], "%Y-%m-%d"
    ).date()
    for day in movie["movie_info_days"]:
        if dt.datetime.strptime(day["date"], "%Y-%m-%d").date() > first_date:
            break
        if day["wikipedia_views"] is None:
            continue
        test_dict["pre_release_cumulative_wikipedia_views"] += day["wikipedia_views"]
        if day["youtube_sum_all_views"] is not None:
            test_dict["youtube_sum_all_views"] = day["youtube_sum_all_views"]
    test_dict["budget"] = movie["budget"]
    test_dict["pre_release_cumulative_wikipedia_views"] = test_dict[
        "pre_release_cumulative_wikipedia_views"
    ]

    test_df = pd.DataFrame(test_dict, index=[0])

    actual = movie["boxofficedays"][0]["revenue"]

    # run the model
    prediction = model.predict(test_df)[0]

    if prediction < 1000:
        prediction = 1000

    return ActualPredicted(
        actual=int(actual),
        predicted=int(prediction),
    )


def get_movie_data(movie_ids: list[str]) -> dict[str, MovieCache]:
    movie_ids_to_get = []
    movie_data: dict[str, MovieCache] = {}

    for movie_id in movie_ids:
        if movie_id in movie_data:
            continue
        if movie_id in movie_id_to_cache:
            movie_cache = movie_id_to_cache[movie_id]
            movie = movie_cache["movie"]
            if movie is None:
                list_movies: list[Movie] = (
                    supabase.table("movie")
                    .select("*")
                    .eq("id", movie_id)
                    .execute()
                    .data
                )
                movie = list_movies[0]
                movie_id_to_cache[movie_id]["movie"] = movie
                movie_data[movie_id] = movie_id_to_cache[movie_id]

            movie_data[movie_id] = movie_cache
        else:
            movie_ids_to_get.append(movie_id)

    if not movie_ids_to_get:
        return movie_data

    try:
        list_movies: list[Movie] = (
            supabase.table("movie")
            .select("*")
            .in_("id", movie_ids_to_get)
            .execute()
            .data
        )
    except ReadError:
        time.sleep(1)
        list_movies: list[Movie] = (
            supabase.table("movie")
            .select("*")
            .in_("id", movie_ids_to_get)
            .execute()
            .data
        )

    boxofficedays: list[Boxofficeday] = (
        supabase.table("boxofficeday")
        .select("*")
        .in_("movie_id", movie_ids_to_get)
        # .eq("is_preview", False)
        .order("date")
        .execute()
        .data
    )

    # switch the first friday to be true friday
    if len(boxofficedays) > 0:
        if boxofficedays[0]["is_preview"] is True and len(boxofficedays) > 1:
            boxofficedays[1]["revenue"] -= boxofficedays[0]["revenue"]

        del boxofficedays[0]

    original_boxofficedays = deepcopy(boxofficedays)

    # adjust the boxofficedays
    for day in boxofficedays:
        day_date = dt.datetime.strptime(day["date"], "%Y-%m-%d").date()
        adjustment = get_adjustment_weight(day_date)
        day["revenue"] = int(day["revenue"] / adjustment)

    movie_info_days: list[MovieInfoDay] = (
        supabase.table("movie_info_day")
        .select("*")
        .in_("movie_id", movie_ids_to_get)
        .order("date")
        .execute()
        .data
    )

    release_dates: list[MovieReleaseDate] = (
        supabase.table("movie_release_date")
        .select("*")
        .in_("movie_id", movie_ids_to_get)
        .neq("release_type", "IMAX")
        # .neq("release_type", "Special Engagement")
        .neq("release_type", "Oscar Qualifying Run")
        .order("release_date")
        .execute()
        .data
    )

    id_to_boxoffice_days: dict[str, list[Boxofficeday]] = defaultdict(list)
    for boxofficeday in boxofficedays:
        id_to_boxoffice_days[boxofficeday["movie_id"]].append(boxofficeday)
    id_to_movie_info_days: dict[str, list[MovieInfoDay]] = defaultdict(list)
    for movie_info_day in movie_info_days:
        id_to_movie_info_days[movie_info_day["movie_id"]].append(movie_info_day)
    id_to_release_dates: dict[str, list[MovieReleaseDate]] = defaultdict(list)
    for release_date in release_dates:
        id_to_release_dates[release_date["movie_id"]].append(release_date)
    id_to_original_boxoffice_days: dict[str, list[Boxofficeday]] = defaultdict(list)
    for boxofficeday in original_boxofficedays:
        id_to_original_boxoffice_days[boxofficeday["movie_id"]].append(boxofficeday)

    for movie in list_movies:
        movie_id = movie["id"]
        if movie_id not in movie_ids_to_get:
            continue
        boxofficedays = id_to_boxoffice_days[movie_id]
        original_boxofficedays = id_to_original_boxoffice_days[movie_id]
        movie_info_days = id_to_movie_info_days[movie_id]
        release_dates = id_to_release_dates[movie_id]

        # create the cache
        movie_id_to_cache[movie_id] = MovieCache(
            movie=movie,
            boxofficedays=boxofficedays,
            original_boxofficedays=original_boxofficedays,
            movie_info_days=movie_info_days,
            release_dates=release_dates,
            budget=movie["budget"] if movie["budget"] is not None else 0,
        )

        # add the cache to the movie_data
        movie_data[movie_id] = movie_id_to_cache[movie_id]

    return movie_data


def get_single_movie_data(
    movie_id: str,
    retries: int = 3,
) -> MovieCache:
    try:
        data = get_movie_data([movie_id])
        if movie_id not in data:
            raise ValueError(f"Movie with id {movie_id} not found")
        return data[movie_id]
    except RemoteProtocolError:
        if retries > 0:
            time.sleep(1)
            return get_single_movie_data(movie_id, retries - 1)
        else:
            raise ValueError(f"Movie with id {movie_id} not found") from None


def get_knn_data(
    movie_id: str,
    k: int = default_k(),
    knn_weights: KNNWeights = default_knn_weights(),
) -> dict[str, MovieCache]:
    knn: list[KNNRPC] = (
        supabase.rpc("knn", {"movie_id_og": movie_id, "k": k, "weights": knn_weights})
        .execute()
        .data
    )
    # get the boxofficedays and movie info days for the knn
    knn_ids: list[str] = [x["return_id"] for x in knn]
    new_knn_ids: list[str] = []

    caches_to_return: dict[str, MovieCache] = {}

    # check the cache for them
    for knn_id in knn_ids:
        if knn_id not in movie_id_to_cache:
            new_knn_ids.append(knn_id)
        else:
            cache = movie_id_to_cache[knn_id]
            caches_to_return[knn_id] = cache

    del knn_ids

    knn_budget_dict: dict[str, TitleBudget] = {
        movie["return_id"]: {"title": movie["title"], "budget": movie["budget"]}
        for movie in knn
    }

    knn_boxofficedays: list[Boxofficeday] = (
        supabase.table("boxofficeday")
        .select("*")
        .in_("movie_id", new_knn_ids)
        # .eq("is_preview", False)
        .order("movie_id")
        .order("date")
        .execute()
        .data
    )

    # switch the first friday to be true friday
    preview_indices = []
    for i, boxofficeday in enumerate(knn_boxofficedays):
        if boxofficeday["is_preview"] is True:
            preview_indices.append(i)
            knn_boxofficedays[i + 1]["revenue"] -= boxofficeday["revenue"]

    # remove the previews
    for i in reversed(preview_indices):
        del knn_boxofficedays[i]

    knn_movie_info_days: list[MovieInfoDay] = (
        supabase.table("movie_info_day")
        .select("*")
        .in_("movie_id", new_knn_ids)
        .order("date")
        .execute()
        .data
    )

    knn_release_dates: Table[MovieReleaseDate] = (
        supabase.table("movie_release_date")
        .select("*")
        .neq("release_type", "IMAX")
        .neq("release_type", "Special Engagement")
        .in_("movie_id", new_knn_ids)
        .order("release_date")
        .execute()
        .data
    )

    for knn_id in new_knn_ids:
        movie: Movie | None = None

        if knn_id in movie_id_to_cache:
            movie = movie_id_to_cache[knn_id]["movie"]
        else:
            list_movies: list[Movie] = (
                supabase.table("movie").select("*").eq("id", knn_id).execute().data
            )
            if len(list_movies) == 0:
                raise ValueError(f"Movie with id {knn_id} not found")
            movie = list_movies[0]

        cache = MovieCache(
            movie=movie,
            boxofficedays=[],
            original_boxofficedays=[],
            movie_info_days=[],
            release_dates=[],
            budget=0,
        )
        cache["boxofficedays"] = [
            x for x in knn_boxofficedays if x["movie_id"] == knn_id
        ]

        cache["original_boxofficedays"] = deepcopy(cache["boxofficedays"])

        # adjust the boxofficedays
        for day in cache["boxofficedays"]:
            day_date = dt.datetime.strptime(day["date"], "%Y-%m-%d").date()
            adjustment = get_adjustment_weight(day_date)
            day["revenue"] = int(day["revenue"] / adjustment)

        cache["movie_info_days"] = [
            x for x in knn_movie_info_days if x["movie_id"] == knn_id
        ]
        cache["release_dates"] = [
            x for x in knn_release_dates if x["movie_id"] == knn_id
        ]
        cache["budget"] = knn_budget_dict[knn_id]["budget"]

        movie_id_to_cache[knn_id] = cache
        caches_to_return[knn_id] = cache

    return caches_to_return


def get_multipliers(
    boxofficedays: list[Boxofficeday],
    release_dates: list[MovieReleaseDate],
    knn_data: dict[str, MovieCache],
    test_days: int | None = None,
    verbose: bool = False,
) -> tuple[
    list[Multiplier],
    list[BetweenReleaseTypeMultiplier],
]:
    mults: list[Multiplier] = []
    between_release_type_mults: list[BetweenReleaseTypeMultiplier] = []

    current_release_day = len(boxofficedays)

    if len(boxofficedays) != 0:
        start_index = 1
        first_day_of_week = dt.datetime.strptime(
            boxofficedays[0]["date"], "%Y-%m-%d"
        ).weekday()

        # if the first day of the week isn't a friday, then we need to start at the first monday -> Tuesday
        if first_day_of_week != 4:
            start_index = (5 - first_day_of_week) % 7
            if verbose:
                print(f"{start_index=}")

        current_release_type_index = 0

        for i, boxofficeday in enumerate(boxofficedays[start_index:test_days], 1):
            weeks_in_past = (current_release_day - i) // 7

            day_date = dt.datetime.strptime(boxofficeday["date"], "%Y-%m-%d").date()
            day_of_week = day_date.weekday()

            prev_day = boxofficedays[i - 1]

            multiplier = boxofficeday["revenue"] / prev_day["revenue"]
            theater_count_multiplier = 1
            if (
                boxofficeday["theaters"] is not None
                and boxofficeday["theaters"] > 0
                and prev_day["theaters"] is not None
                and prev_day["theaters"] > 0
            ):
                theater_count_multiplier = (
                    boxofficeday["theaters"] / prev_day["theaters"]
                )

            if (
                current_release_type_index < len(release_dates) - 1
                and day_date
                >= dt.datetime.strptime(
                    release_dates[current_release_type_index + 1]["release_date"],
                    "%Y-%m-%d",
                ).date()
            ):
                current_release_type_index += 1

                prior_release_type = release_dates[current_release_type_index - 1][
                    "release_type"
                ]
                current_release_type = release_dates[current_release_type_index][
                    "release_type"
                ]
                between_release_type_mults.append(
                    {
                        "multiplier": multiplier,
                        "start_release_type": prior_release_type,
                        "end_release_type": current_release_type,
                        "start_theater_count": (
                            prev_day["theaters"]
                            if prev_day["theaters"] is not None
                            else 1
                        ),
                        "end_theater_count": (
                            boxofficeday["theaters"]
                            if boxofficeday["theaters"] is not None
                            else 1
                        ),
                        "end_days_after_first_friday": i,
                    }
                )
                continue  # if the release type changes, we don't want to add a multiplier

                #
            if current_release_type_index >= len(release_dates):
                # skip the movie since it doesn't have release dates
                print(
                    bcolors.WARNING +
                    f"Skipping {boxofficeday['movie_id']} since it doesn't have release dates {len(release_dates)=}" +
                    bcolors.ENDC
                )
                continue
            mults.append(
                {
                    "end_weekday": day_of_week % 7,
                    "multiplier": multiplier,
                    "weight": 10,
                    "end_days_after_first_friday": i,
                    "release_type": release_dates[current_release_type_index][
                        "release_type"
                    ],
                    "theater_count_multiplier": theater_count_multiplier,
                }
            )

    for movie_id, cache_value in knn_data.items():
        knn_boxofficedays = cache_value["boxofficedays"]
        movie_release_dates = cache_value["release_dates"]
        if verbose:
            print(f"{movie_release_dates=}, {movie_id=}")
            print(f"Processing KNN {movie_id} with {len(knn_boxofficedays)} box office days")

        if len(knn_boxofficedays) == 0:
            print(f"Skipping KNN {movie_id} since it doesn't have box office data")
            continue

        first_day_of_week = dt.datetime.strptime(
            knn_boxofficedays[0]["date"], "%Y-%m-%d"
        ).weekday()

        current_release_type_index = 0

        if current_release_type_index >= len(movie_release_dates):
            # skip the KNN movie since it doesn't have release dates
            print(
                f"Skipping {movie_id} since it doesn't have release dates {len(movie_release_dates)=}"
            )
            continue

        current_release_type = movie_release_dates[current_release_type_index][
            "release_type"
        ]

        # if the first day of the week isn't a friday, then we need to start at the first monday -> Tuesday
        # if first_day_of_week is Friday so 4, we would want the start_index to be 1
        # if first_day_of_week is Tuesday so 1, we would want the start_index to be 4
        # if first_day_of_week is Wednesday so 2, we would want the start_index to be 3
        # if first_day_of_week is Saturday so 5, we would want the start_index to be 6
        start_index = 1
        if first_day_of_week != 4:
            start_index = (5 - first_day_of_week) % 7
            if verbose:
                print("Start index", start_index)

        for i, current_day in enumerate(knn_boxofficedays[start_index:], 1):
            current_date = dt.datetime.strptime(current_day["date"], "%Y-%m-%d").date()
            day_of_week = current_date.weekday()

            prev_revenue = knn_boxofficedays[i - 1]["revenue"]

            if prev_revenue == 0:
                prev_revenue = 1

            multiplier = current_day["revenue"] / prev_revenue

            prior_theaters = knn_boxofficedays[i - 1]["theaters"]
            if prior_theaters is None:
                prior_theaters = 1
            current_theaters = current_day["theaters"]
            if current_theaters is None:
                current_theaters = 1

            if (
                current_release_type_index < len(movie_release_dates) - 1
                and current_date
                >= dt.datetime.strptime(
                    movie_release_dates[current_release_type_index + 1]["release_date"],
                    "%Y-%m-%d",
                ).date()
            ):
                current_release_type_index += 1

                prior_release_type = movie_release_dates[
                    current_release_type_index - 1
                ]["release_type"]
                current_release_type = movie_release_dates[current_release_type_index][
                    "release_type"
                ]

                between_release_type_mults.append(
                    {
                        "multiplier": multiplier,
                        "start_release_type": prior_release_type,
                        "end_release_type": current_release_type,
                        "start_theater_count": prior_theaters,
                        "end_theater_count": current_theaters,
                        "end_days_after_first_friday": i,
                    }
                )

                continue  # if the release type changes, we don't want to add a multiplier

            release_type = movie_release_dates[current_release_type_index][
                "release_type"
            ]
            weeks_diff = (current_release_day - i) // 7
            mults.append(
                {
                    "end_weekday": day_of_week % 7,
                    "multiplier": multiplier,
                    "weight": 1.5 ** (-abs(weeks_diff) + 1),
                    "end_days_after_first_friday": i,
                    "release_type": release_type,
                    "theater_count_multiplier": prior_theaters / current_theaters,
                }
            )

    if verbose:
        # save mults to a json file
        with open("mults.json", "w") as f:
            import json

            json.dump(mults, f)

    return mults, between_release_type_mults


def predict_movie(
    movie_id: str,
    test_days: int | None = None, # if test days is None, use all the data
    verbose: bool = False,
    k: int = default_k(),
    weights: KNNWeights = default_knn_weights(),
) -> MoviePredictions:
    """
    Returns previous values and then new predictions
    """
    """
    Also for right now this function ignores holidays, seasons, limited releases, and movies opening on weekdays
    """
    """
    Given a movie id return a time series list of predicted box office revenue until it leaves theaters
    """
    MAX_PREDICTION_DAYS = 120
    movie_data = get_single_movie_data(movie_id)
    knn_data = get_knn_data(movie_id, k, weights)

    # most basic predictions to start. Eventually implement theater counts, previews, reviews, wikipedia views, holidays, seasons, opening day of week, limited release
    # to make the predictions simply get the expected drop coefficients for each day and then apply

    mults, between_release_type_mults = get_multipliers(
        movie_data["boxofficedays"],
        movie_data["release_dates"],
        knn_data,
        test_days=test_days,
        verbose=verbose,
    )

    ################## Also want to calculate the daily worsening in multipliers as a movie is in theaters longer
    # get the weekly drops
    weekly_grosses: dict[str, list[float]] = {}  # knn_id -> list of weekly grosses
    for key, value in knn_data.items():
        knn_boxofficedays = value["boxofficedays"]
        if key not in weekly_grosses:
            weekly_grosses[key] = []

        if verbose:
            print(f"{key=}, {len(knn_boxofficedays)=}, {value['movie']['title']=}")

        for i, boxofficeday in enumerate(knn_boxofficedays):
            week = i // 7

            if i % 7 == 0:
                weekly_grosses[key].append(boxofficeday["revenue"])
            else:
                weekly_grosses[key][week] += boxofficeday["revenue"]

    # print the median value of the drop by week
    drops_by_week_values: list[list[float]] = []
    for key, value in weekly_grosses.items():
        drops_by_week = [value[i] / value[i - 1] for i in range(1, len(value))]
        drops_by_week_values.append(drops_by_week)

    weekly_drops_to_use = []
    max_length_of_drops = max([len(x) for x in drops_by_week_values])

    # add drops by week for the movie to predict if it has been out for more than 7 days
    # if the target movie has been out for more than a week also add it
    if len(movie_data["boxofficedays"]) >= 7:
        movie_weekly_grosses: list[float] = []
        for i, boxofficeday in enumerate(movie_data["boxofficedays"]):
            week = i // 7  # add it in the future

            if i % 7 == 0:
                movie_weekly_grosses.append(boxofficeday["revenue"])
            else:
                movie_weekly_grosses[week] += boxofficeday["revenue"]
        movie_drops_by_week = [
            movie_weekly_grosses[i] / movie_weekly_grosses[i - 1]
            for i in range(1, len(movie_weekly_grosses))
        ]
        for i in range(max_length_of_drops - len(movie_drops_by_week)):
            movie_drops_by_week = [np.nan] + movie_drops_by_week
            for i in range(2):  # add it twice for more impact on median
                drops_by_week_values.append(movie_drops_by_week)

    for i in range(max_length_of_drops):
        median_values = []
        for x in drops_by_week_values:
            if len(x) > i:
                if not np.isnan(x[i]):
                    median_values.append(x[i])
            else:
                median_values.append(0)

        weekly_drops_to_use.append(np.median(median_values))
    if verbose:
        print(f"{weekly_drops_to_use=}")

    # graph the weekly grosses
    # for key, value in weekly_grosses.items():
    #     plt.plot(range(len(value)), value, label=key)
    # plt.title("Weekly grosses")
    # plt.legend()
    # plt.show()

    # print(mults)

    # now we have the multipliers, take a weighted average of the multipliers
    # the weights are the weight of the multiplier

    multipliers_information_by_release_type_7: dict[str, list[tuple[float, float]]] = {}
    multipliers_information_by_release_type_full: dict[str, list[list[float]]] = {}
    """
    Responsible for applying the weights.
    The first number in the tuple is the weighted sum of the multipliers
    The second number in the tuple is the sum of the weights
    """

    for mult in mults:
        if mult["release_type"] not in multipliers_information_by_release_type_7:
            multipliers_information_by_release_type_7[mult["release_type"]] = [
                (0, 0) for _ in range(7)
            ]

        multipliers_information_by_release_type_7[mult["release_type"]][
            mult["end_weekday"]
        ] = (
            multipliers_information_by_release_type_7[mult["release_type"]][
                mult["end_weekday"]
            ][0]
            + mult["multiplier"] * mult["weight"],
            multipliers_information_by_release_type_7[mult["release_type"]][
                mult["end_weekday"]
            ][1]
            + mult["weight"],
        )

        if mult["end_days_after_first_friday"] >= MAX_PREDICTION_DAYS:
            continue

        if mult["release_type"] not in multipliers_information_by_release_type_full:
            multipliers_information_by_release_type_full[mult["release_type"]] = []
            for i in range(MAX_PREDICTION_DAYS):
                multipliers_information_by_release_type_full[
                    mult["release_type"]
                ].append([])

        multipliers_information_by_release_type_full[mult["release_type"]][
            mult["end_days_after_first_friday"]
        ].append(mult["multiplier"])

    if verbose:
        print(f"{multipliers_information_by_release_type_7=}")

    multiplier_values_by_release_type_7: dict[str, list[float]] = {}
    multiplier_values_by_release_type_full: dict[str, list[float]] = {}

    for key, value in multipliers_information_by_release_type_7.items():
        multiplier_values_by_release_type_7[key] = [
            x[0] / x[1] for x in value if x[1] > 0  # weighted average
        ]

    for key, value in multipliers_information_by_release_type_full.items():
        multiplier_values_by_release_type_full[key] = [
            np.median(x) for x in value if len(x) > 0
        ]

    combined_mult_by_release_type_7: dict[str, float] = {}
    for key, value in multiplier_values_by_release_type_7.items():
        combined_mult_by_release_type_7[key] = float(np.prod(value))

    # the combined multiplier needs to be 1
    for key, value in multiplier_values_by_release_type_7.items():
        combined = combined_mult_by_release_type_7[key]
        multiplier_values_by_release_type_7[key] = [
            x * (1 / combined) ** (1 / 7) for x in value
        ]

    multipliers_between_release_types: dict[tuple[str, str], list[float]] = {}
    for mult in between_release_type_mults:
        if (
            mult["start_release_type"],
            mult["end_release_type"],
        ) not in multipliers_between_release_types:
            multipliers_between_release_types[
                (mult["start_release_type"], mult["end_release_type"])
            ] = []

        multipliers_between_release_types[
            (mult["start_release_type"], mult["end_release_type"])
        ].append(mult["multiplier"] * mult["end_days_after_first_friday"])
    multiplier_values_between_release_types: dict[tuple[str, str], float] = {}
    for key, value in multipliers_between_release_types.items():
        multiplier_values_between_release_types[key] = float(np.median(value))

    current_release_type_index = -1
    release_dates = movie_data["release_dates"]
    if len(release_dates) == 0:
        raise ValueError(
            f"No release dates found for movie {movie_data['movie']['title']}, {movie_id=}"
        )
    current_release_type = release_dates[current_release_type_index]["release_type"]
    current_release_type_date: dt.date = dt.datetime.strptime(
        release_dates[current_release_type_index]["release_date"], "%Y-%m-%d"
    ).date()
    boxofficedays = movie_data["boxofficedays"]
    original_boxofficedays = movie_data["original_boxofficedays"]

    if test_days is not None:
        max_days = test_days
    else:
        max_days = len(boxofficedays) - 1
    if max_days >= len(boxofficedays):
        max_days = len(boxofficedays) - 1
    if (max_days > 0 or test_days is None) and len(boxofficedays) > 0:
        # now we have the multipliers for each day of the week
        # now we can predict the box office revenue until it drops under $5000
        most_recent_revenue = boxofficedays[max_days]["revenue"]  # this is adjusted
        most_recent_date: dt.date = dt.datetime.strptime(
            boxofficedays[max_days]["date"], "%Y-%m-%d"
        ).date()
    else:
        most_recent_date = current_release_type_date

        most_recent_revenue = predict_opening_day(movie_data, most_recent_date)

    days_out = 0

    predicted_date = most_recent_date

    start_predictions_date = most_recent_date

    print(f"Start predictions date: {start_predictions_date} with max days {max_days}")

    predicted_revenue: list[int] = []

    while most_recent_revenue > 5000 and len(predicted_revenue) < MAX_PREDICTION_DAYS:
        if days_out // 7 >= len(weekly_drops_to_use):
            if verbose:
                print("No more weekly drops to use")
                print(f"{days_out=}, {weekly_drops_to_use=}")
            break

        in_between_multiplier = 1
        # check for the current release type
        if (
            len(release_dates) > current_release_type_index + 1
            and predicted_date >= current_release_type_date
        ):
            current_release_type_index += 1
            current_release_type = release_dates[current_release_type_index][
                "release_type"
            ]
            current_release_type_date = dt.datetime.strptime(
                release_dates[current_release_type_index]["release_date"], "%Y-%m-%d"
            ).date()

            if (
                current_release_type_index > 0
                and (
                    previous_release_type := release_dates[
                        current_release_type_index - 1
                    ]["release_type"]
                )
                != current_release_type
            ):
                pass
                # in_between_multiplier = multiplier_values_between_release_types[
                #     (previous_release_type, current_release_type)
                # ] / days_out

        weekly_dropping = weekly_drops_to_use[days_out // 7]
        daily_drop = weekly_dropping ** (1 / 7)

        if current_release_type not in multiplier_values_by_release_type_7:
            key_list = list(multiplier_values_by_release_type_7.keys())
            if len(key_list) == 0:
                print(
                    f"Release type {current_release_type} not found for movie {movie_data['movie']['title']}"
                )
                break
            current_release_type = list(multiplier_values_by_release_type_7.keys())[-1]
        relevant_multiplier_values = multiplier_values_by_release_type_7[
            current_release_type
        ]

        if predicted_date.weekday() >= len(relevant_multiplier_values):
            print(
                f"Predicted date {predicted_date} is out of range for {current_release_type} for movie {movie_data['movie']['title']}"
            )
            break
        multiplier = relevant_multiplier_values[predicted_date.weekday()]

        if current_release_type not in multiplier_values_by_release_type_full:
            current_release_type = list(multiplier_values_by_release_type_full.keys())[
                -1
            ]

        full_values_by_release_type = multiplier_values_by_release_type_full[
            current_release_type
        ]
        release_type_length = len(full_values_by_release_type)

        days_out_to_use = days_out
        while days_out_to_use >= release_type_length:
            days_out_to_use -= 7

        # multiplier = full_values_by_release_type[days_out_to_use]
        # daily_drop = 1

        most_recent_revenue = int(
            most_recent_revenue * multiplier * daily_drop * in_between_multiplier
        )  # this is an adjusted value
        adjustment = get_adjustment_weight(predicted_date)
        predicted_revenue.append(int(most_recent_revenue * adjustment))
        days_out += 1

        if verbose:
            print(
                "Multiplier from adjusted",
                round(multiplier, 3),
                "Multiplier from original",
                round(
                    (
                        predicted_revenue[-1] / predicted_revenue[-2]
                        if len(predicted_revenue) > 1
                        else predicted_revenue[-1]
                        / original_boxofficedays[max_days]["revenue"]
                    ),
                    3,
                ),
                "daily drop",
                round(daily_drop, 3),
                "date",
                predicted_date,
                "weekday",
                predicted_date.weekday(),
            )

        predicted_date += dt.timedelta(days=1)
    if movie_data["movie"] is None:  # it will always be found
        raise ValueError("Movie not found")

    if len(predicted_revenue) == 0:
        predicted_revenue = [0]

    try:
        return MoviePredictions(
            existing=[x["revenue"] for x in boxofficedays[:max_days]],
            predicted=predicted_revenue,
            actual=[x["revenue"] for x in original_boxofficedays[max_days:]],
            movie=movie_data["movie"],
            start_predictions_date=start_predictions_date,
        )
    except Exception as e:
        print(f"Error in predict_movie: {e}")
        print(f"{movie_data=}")
        raise e


def add_poster_to_graph(
    ax: Axes,
    movie: Movie,
):
    # read in the poster for the movie
    poster_path = movie["poster_path"]
    if poster_path is not None:
        poster_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
        response = S.get(poster_path)
        if response.status_code == 200:
            axins = inset_axes(
                ax,
                width="100%",
                height="100%",
                loc="center right",
                bbox_transform=ax.transAxes,
                bbox_to_anchor=(
                    0.67,
                    0.39,
                    0.5,
                    0.42,
                ),  # https://stackoverflow.com/questions/4700614/how-to-put-the-legend-outside-the-plot/43439132#43439132
            )
            img = Image.open(BytesIO(response.content))
            img = img.resize((350, 525))
            axins.imshow(img)
            axins.axis("off")


def graph_predictions(
    existing: list[int],
    predicted: list[int],
    actual: list[int],
    movie: Movie,
    test_days: int,
):
    # divide all values by 1_000_000
    metrics = get_metrics(actual, predicted)
    existing_scaled = [x / 1_000_000 for x in existing]
    predicted_scaled = [x / 1_000_000 for x in predicted]
    actual_scaled = [x / 1_000_000 for x in actual]

    # plot the existing data
    fig, ax = plt.subplots(figsize=(20, 12))

    days_in_release = list(range(len(existing_scaled)))

    if len(existing_scaled) == 1:
        sns.scatterplot(
            x=days_in_release,
            y=existing_scaled,
            label="Given data",
            color="red",
            markers="o",
        )
    else:
        sns.lineplot(
            x=days_in_release,
            y=existing_scaled,
            label="Given data",
            color="red",
            markers="o",
        )
    sns.lineplot(
        x=range(len(existing_scaled), len(predicted_scaled) + len(existing_scaled)),
        y=predicted_scaled,
        label="Predicted",
        color="blue",
    )
    sns.lineplot(
        x=range(len(existing_scaled), len(actual_scaled) + len(existing_scaled)),
        y=actual_scaled,
        label="Actual",
        color="green",
    )

    # add tooltips
    cursor(hover=True)

    plt.xlabel("Days in Release", fontsize=20)
    plt.ylabel("Revenue (in Millions)", fontsize=20)
    plt.title(
        f"Gerber Method Predicted Revenue for $\\it{{ {movie['title'].replace(" ", "~")} }}$ Given {test_days} Day{'s' if test_days > 1 else ''}",
        fontsize=24,
    )
    plt.legend(loc="upper right", fontsize=20)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    # text for mape, rmse, mapd
    plt.text(
        0.88,
        0.15,
        f"WMAPD: {metrics.wmapd:.2%}\nMAPD: {metrics.mapd:.2%}",
        fontsize=16,
        ha="left",
        va="center",
        transform=plt.gca().transAxes,
    )

    # bottom left text for release date
    release_date = movie["release_date"]
    if release_date is not None:
        release_date = dt.datetime.strptime(release_date, "%Y-%m-%d").date()
        plt.text(
            0.01,
            0.01,
            f"Release date: {release_date}",
            fontsize=20,
            ha="left",
            va="bottom",
            transform=plt.gca().transAxes,
        )

    add_poster_to_graph(ax, movie)

    # save the figure
    base_dir = os.getenv("BASE_DIR")

    if base_dir is not None:
        filename = os.path.join(
            base_dir,
            "shared",
            "images",
            "pred",
        )

        plt.savefig(
            f"{filename}/{movie['title']}_{test_days}.png", dpi=300, bbox_inches="tight"
        )

    plt.show()


class PredictionDaysGiven(TypedDict):
    predictions: list[int]
    day_given: int


def graph_predictions_multiple(
    predictions: list[PredictionDaysGiven],
    actual: list[int],
    movie: Movie,
):
    MIN_VALUE = 1500
    scale = 1  # don't scale cause using log scale
    actual_scaled = [x / scale for x in actual]
    predictions_scaled = [
        [x / scale for x in prediction["predictions"]] for prediction in predictions
    ]

    print(f"{actual_scaled=}, {predictions_scaled=}")

    # minimum y value
    max_y_value = max(actual_scaled)
    max_y_pred = max(
        [max(prediction_scaled) for prediction_scaled in predictions_scaled]
    )
    max_y = max(max_y_value, max_y_pred)

    # plot the existing data
    fig, ax = plt.subplots(figsize=(20, 12))

    # log scale
    plt.yscale("log")
    plt.ylim(MIN_VALUE, max_y * 1.1)

    days_in_release = list(range(len(actual_scaled)))
    sns.lineplot(
        x=days_in_release,
        y=actual_scaled,
        label="Actual",
        color="green",
    )
    cursor(hover=True)

    # plt.xlim(0, max_x)
    # plt.ylim(0, max_y * 1.1)
    plt.xlabel("Days in Release", fontsize=20)
    plt.ylabel("Revenue (log scale)", fontsize=20)
    plt.title(
        f"Gerber Method Predicted Revenue for $\\it{{ {movie['title'].replace(' ', '~')} }}$",
        fontsize=24,
    )
    plt.legend(loc="upper right", fontsize=48)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    # release date
    release_date = movie["release_date"]
    if release_date is not None:
        release_date = dt.datetime.strptime(release_date, "%Y-%m-%d").date()
        plt.text(
            0.01,
            0.01,
            f"Release date: {release_date}",
            fontsize=16,
            ha="left",
            va="bottom",
            transform=plt.gca().transAxes,
        )

    max_x = max(days_in_release)
    max_y = max(actual_scaled)

    add_poster_to_graph(ax, movie)

    def save_image(counter=0):
        base_dir = os.getenv("BASE_DIR")

        if base_dir is not None:
            filename = os.path.join(
                base_dir,
                "shared",
                "images",
                "pred",
            )

            plt.savefig(
                f"{filename}/{movie['title']}_multiple_{counter}.png",
                dpi=300,
                bbox_inches="tight",
            )
        else:
            print("No base dir found, not saving image")

    plt.text(
        0.88,
        0.24,
        f"WMAPD",
        fontsize=16,
        ha="left",
        va="center",
        transform=ax.transAxes,
    )
    for i, prediction in enumerate(predictions):
        prediction_scaled = predictions_scaled[i]
        days_given = prediction["day_given"]

        day_or_days = "Day" if days_given == 1 else "Days"

        sns.lineplot(
            x=range(
                days_given,
                days_given + len(prediction_scaled),
            ),
            y=prediction_scaled,
            label=f"Predicted {days_given} {day_or_days} Given",
            color=(0.5, 0.2, 0.8, (i + 1) / len(predictions)),
            ax=ax,
        )

        max_x = max(max_x, days_given + len(prediction_scaled))
        max_y = max(max_y, max(prediction_scaled))

        metrics = get_metrics(actual[days_given:], prediction["predictions"])

        plt.text(
            0.87,
            0.20 - i * 0.04,
            f"{days_given} {day_or_days}: {metrics.wmapd:.2%}",
            fontsize=16,
            ha="left",
            va="center",
            transform=ax.transAxes,
        )

        save_image(i + 1)

    plt.show()


def get_mape(actual: list[int], predicted: list[int]) -> float:
    max_len = min(len(actual), len(predicted))
    actual = actual[:max_len]
    predicted = predicted[:max_len]

    return float(
        np.mean([abs(actual[i] - predicted[i]) / actual[i] for i in range(len(actual))])
    )


def get_mapd(actual: list[int], predicted: list[int]) -> float:
    max_len = min(len(actual), len(predicted))
    actual = actual[:max_len]
    predicted = predicted[:max_len]

    return float(
        np.mean(
            [
                abs(actual[i] - predicted[i]) / (actual[i] + predicted[i])
                for i in range(len(actual))
            ]
        )
    )


def get_rmse(actual: list[int], predicted: list[int]) -> float:
    max_len = min(len(actual), len(predicted))
    actual = actual[:max_len]
    predicted = predicted[:max_len]

    return np.sqrt(
        np.mean([(actual[i] - predicted[i]) ** 2 for i in range(len(actual))])
    )


def get_sum_absolute_error(actual: list[int], predicted: list[int]) -> float:
    max_len = min(len(actual), len(predicted))
    actual = actual[:max_len]
    predicted = predicted[:max_len]

    return float(np.sum([abs(actual[i] - predicted[i]) for i in range(len(actual))]))


def get_weighted_mapd(actual: list[int], predicted: list[int]) -> float:
    """
    The mean absolute percentage difference where each term is weighted by the sum of the existing and predicted values
    """
    print(f"{actual=}, {predicted=}")
    max_len = min(len(actual), len(predicted))
    actual = actual[:max_len]
    predicted = predicted[:max_len]

    mapd_values = [abs(actual[i] - predicted[i]) for i in range(len(actual))]

    divisor = np.sum([actual[i] + predicted[i] for i in range(len(actual))])

    return float(np.sum(mapd_values) / divisor)


def get_weighted_mapd_by_index(actual: list[int], predicted: list[int]) -> float:
    """
    The mean absolute percentage difference where each term is weighted by the sum of the existing and predicted values
    """
    max_len = min(len(actual), len(predicted))
    actual = actual[:max_len]
    predicted = predicted[:max_len]

    mapd_values = [
        abs(actual[i] - predicted[i]) / (actual[i] + predicted[i])
        for i in range(len(actual))
    ]

    weights = [len(actual) - i for i in range(len(actual))]

    return float(
        np.average(
            mapd_values,
            weights=weights,
        )
    )


def get_metrics(actual: list[int], predicted: list[int]) -> PredictionMetrics:
    mape = get_mape(actual, predicted)
    rmse = get_rmse(actual, predicted)
    mapd = get_mapd(actual, predicted)
    wmapd = get_weighted_mapd(actual, predicted)
    sae = get_sum_absolute_error(actual, predicted)
    wmapd_by_index = get_weighted_mapd_by_index(actual, predicted)

    return PredictionMetrics(
        mape=mape,
        rmse=rmse,
        mapd=mapd,
        wmapd=wmapd,
        sae=sae,
        wmapd_by_index=wmapd_by_index,
    )


if __name__ == "__main__":
    alita_id = "5a8413f0-4d4c-4a3c-a08d-9b3787b8244a"
    drstrange_id = "f8dcab9c-6711-4582-a3d3-5a2a8122b598"
    paddington2_id = "5f507808-3a2c-4690-8367-fcb0d86e4bcc"
    paddington3_id = "7f76ffe4-3621-4e95-bbcb-f84705dfc6df"
    holdovers_id = "58c0cc1e-76b0-473d-8622-b778cf679cb7"
    meangirls_id = "1a1a4ae1-d629-4622-b9f6-701c72aeece2"
    thewhale_id = "e17a39c7-4ea3-449f-b570-2a86d570a28d"
    fallguy_id = "acbfaec1-f445-46f0-bd8f-b710eefbcb30"
    redone_id = "0421bf53-3795-41e1-93fb-5ab2cbdadfa6"
    endgame_id = "88d1658c-1f87-4c5a-91c5-ab754a142c9a"
    dune2_id = "94d9b521-84fc-4741-b5be-72b9e34c272f"
    asteroid_city_id = "e9a7a120-cbca-40a7-bb6b-cf7f8ba063f4"
    last_showgirl_id = "e8103332-288f-4a5a-835d-7ed5c7a5e667"
    queer_id = "39e80dd2-17ef-4732-baf9-7b8dc9db423f"
    love_hurts_id = "b07a43da-3c07-460c-b1da-f881ad18baba"

    # results for the paper
    cap4_id = "65bda6f7-2cba-4154-85b8-a8c1c27aa4ad"  # really good
    anora_id = "459ac5a4-ce5d-4b52-84d7-7b21e13629bf"
    joker_2_id = "7e4f5bed-111f-4fb3-bc3a-ec105f1fc8a1"  # really bad
    terrifier_3_id = "ed984868-d973-4073-a6be-32482aa5b4af"
    alien_romulus_id = "2cd41cae-d2ea-440f-b2f0-9b73d3f9d09d"
    twisters_id = "97ab9d16-90c2-4901-b33a-159448ba2579"
    reagan_id = "644cf330-949f-4196-9309-24c758d688d4"
    transformers_one_id = "fd037aa4-f5e0-4c8d-9e7b-3b4bccd27c16"
    wild_robot_id = "98db73ba-20fe-42c9-8ec2-afa895ce1825"
    mufasa_id = "a8ceb1ec-2f44-413e-b290-06ede35d42e7"
    conclave_id = "70deef7a-03b7-4001-b91e-10ea3cb6eb7f"
    lotr_rohirrim_id = "ab0ca1fd-ea64-494d-a638-c49ab0b1fd96"
    sonic_3_id = "53fcfaaa-09c3-4d9e-9a9b-1dfd35c300cb"
    monkey_man_id = "1af67a76-98e4-4f52-a750-d5cd94aa2167"
    elemental_id = "19e97669-ad94-4d53-82ec-98a4727e733b"
    chhaava_id = "6ed5a859-524f-4443-ad0d-cd914c807fce"
    zoopocalypse_id = "2ba933d0-be8f-4bdb-bee5-ce42605ad1a4"
    one_of_them_days_id = "b19cc39d-e6e6-4e37-962a-9d01d9313121"
    challengers_id = "5fc16a53-33e4-4e3a-a6d3-c24d4bf1dad0"
    barbie_id = "41342557-1869-4c23-b844-1fce4d05e652"
    real_pain_id = "01c1a71a-a058-4b1c-a656-72af4176ab5f"
    nosferatu_id = "017967b6-cc2b-40eb-b763-062bdcd8abf9"
    gladiator_2_id = "e3fa083c-f62b-4a90-b4a2-1e2119db42fb"
    eras_tour_id = "b273f95a-588d-46a7-95f6-012da352e30b"
    megalopolis_id = "1604f3a2-cca9-4e6e-90c4-2c7aca0699f3"
    lee_id = "15b5c8cc-83d9-47ac-866e-c8064123e9ef"
    kinds_of_kindness_id = "c6a6aa01-36a9-4b34-956c-b0eb7b508e12"
    trap_id = "6c9def7e-5853-4d88-be4b-459a14876b37"
    beetlejuice_2_id = "839450a1-599a-4c42-a3f9-8ef4d676cb33"
    inside_out_2_id = "f9a04397-9d1a-4de4-86ef-fb469d008e50"
    sinners_id = "6d7a1df9-9e37-4a46-8755-d3a96f7c8700"
    king_of_kings_id = "844ae03b-e8c1-42a0-918f-32ffcedeeb92"
    smurfs_id = "24d2ba5d-e1dc-49d4-b06a-8ef0ce42f96a"

    do_multiple = False
    id_to_use = smurfs_id

    if not do_multiple:
        test_days = 1
        prediction = predict_movie(id_to_use, test_days, verbose=True)
        graph_predictions(
            prediction.existing,
            prediction.predicted,
            prediction.actual,
            prediction.movie,
            test_days,
        )
    else:
        test_days = [0, 1, 7, 14]
        predictions = [(predict_movie(id_to_use, i), i) for i in test_days]

        graph_predictions_multiple(
            [
                {
                    "predictions": x[0].predicted,
                    "day_given": x[1],
                }
                for x in predictions
            ],
            predictions[0][0].actual,
            predictions[0][0].movie,
        )
