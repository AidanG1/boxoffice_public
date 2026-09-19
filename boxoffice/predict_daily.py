from colors import bcolors
from command_wrapper import wrap_command
from database.db import supabase
from predict import predict_movie
from today import get_today
from typing import TypedDict
import datetime as dt


class MoviePredictionToAdd(TypedDict):
    movie_id: str
    start_date: str
    made_on_date: str
    predictions: list[int]


class MoviePredictionToUpdate(MoviePredictionToAdd):
    id: str


def get_movies_to_predict() -> (
    tuple[list[MoviePredictionToAdd], list[MoviePredictionToUpdate]]
):
    # predict movies that have box office days from yesterday and also movies that have release dates in the future
    today = get_today()

    past_5_days = [today - dt.timedelta(days=i) for i in range(1, 6)]

    # get movies that have box office days from any of the past 5 days
    yesterday_movies = (
        supabase.table("boxofficeday")
        .select("movie_id")
        .in_("date", past_5_days)
        .execute()
        .data
    )

    # get movies that have release dates in the future
    future_movies = (
        supabase.table("movie_release_date")
        .select("movie_id")
        .gt("release_date", today)
        .execute()
        .data
    )

    predict_set = set()
    for movie in yesterday_movies:
        predict_set.add(movie["movie_id"])

    for movie in future_movies:
        predict_set.add(movie["movie_id"])

    # get all existing predictions for the current made on date
    made_on_date = dt.date.strftime(today, "%Y-%m-%d")
    existing_predictions = (
        supabase.table("movie_prediction")
        .select("id, movie_id")
        .eq("made_on_date", made_on_date)
        .execute()
        .data
    )

    predictions_to_make: dict[str, str | None] = (
        {}
    )  # movie_id -> existing prediction id

    for movie in predict_set:
        predictions_to_make[movie] = None

    for pred in existing_predictions:
        predictions_to_make[pred["movie_id"]] = pred["id"]

    predictions: list[MoviePredictionToAdd] = []
    updates: list[MoviePredictionToUpdate] = []

    for movie_id, existing_prediction_id in predictions_to_make.items():
        try:
            prediction = predict_movie(movie_id, None)
        except ValueError as e:
            print(f"{bcolors.FAIL}Error predicting {movie_id}: {e}{bcolors.ENDC}")
            continue
        if existing_prediction_id is not None:
            updates.append(
                {
                    "id": existing_prediction_id,
                    "movie_id": movie_id,
                    "start_date": dt.date.strftime(
                        prediction.start_predictions_date, "%Y-%m-%d"
                    ),
                    "made_on_date": made_on_date,
                    "predictions": prediction.predicted,
                }
            )
        else:
            predictions.append(
                {
                    "movie_id": movie_id,
                    "start_date": dt.date.strftime(
                        prediction.start_predictions_date, "%Y-%m-%d"
                    ),
                    "made_on_date": made_on_date,
                    "predictions": prediction.predicted,
                }
            )

        print(
            f"{bcolors.OKCYAN}Predicted {movie_id} with {len(prediction.predicted)} predictions{bcolors.ENDC}"
        )

    return predictions, updates


def add_predictions_to_database(
    predictions: list[MoviePredictionToAdd], updates: list[MoviePredictionToUpdate]
) -> None:
    if len(predictions) == 0 and len(updates) == 0:
        print(f"{bcolors.WARNING}No predictions to add or update{bcolors.ENDC}")
        return

    if len(predictions) > 0:
        response = supabase.table("movie_prediction").insert(predictions).execute().data

        print(
            f"{bcolors.OKGREEN}Added {len(response)} predictions to the database{bcolors.ENDC}"
        )
    else:
        print(f"{bcolors.WARNING}No new predictions to add{bcolors.ENDC}")

    if len(updates) > 0:
        update_response = (
            supabase.table("movie_prediction").upsert(updates).execute().data
        )
        print(
            f"{bcolors.OKGREEN}Updated {len(update_response)} predictions in the database{bcolors.ENDC}"
        )
    else:
        print(f"{bcolors.WARNING}No updates to make{bcolors.ENDC}")


def full_prediction_pipeline() -> None:
    """
    Runs the full prediction pipeline.
    """
    predictions, updates = get_movies_to_predict()
    add_predictions_to_database(predictions, updates)


if __name__ == "__main__":
    wrap_command(full_prediction_pipeline)
