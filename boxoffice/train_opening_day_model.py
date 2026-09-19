from database.types import OpeningDayDataRPC
from database.db import supabase
import pandas as pd
import statsmodels.api  as sm

if __name__ == "__main__":
    opening_day_data: OpeningDayDataRPC = (
        supabase.rpc("opening_day_data")
        .execute()
        .data
    )

    # convert to a dataframe
    opening_day_df = pd.DataFrame(opening_day_data)

    # then use a robust linear regression model
    formula = "opening_day_revenue ~ 0 + budget + pre_release_cumulative_wikipedia_views : in_franchise"

    model = sm.RLM.from_formula(
        formula,
        data=opening_day_df,
    ).fit()

    # save the model
    model.save("boxoffice/opening_day_model.pkl")