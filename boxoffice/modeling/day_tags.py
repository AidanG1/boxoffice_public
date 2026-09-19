import datetime as dt
from modeling.calculate_day_tags import get_day_tag_data, get_day_tags, get_days_since_first_friday


"""
CORE GOAL: cancel out the effects of time of year and holiday on box office revenue.
This allows for comparison of movies that are released at different times of the year and on different holidays.
Want to leave the effects of the day of the week in the data.

Plan of action:
1. get the median cumulative box office for each day of the year and day since the first friday of the year
2. use cumulative budget * theater count as a proxy for expected box office revenue
3. divide those 2 numbers by each other to get the difference between revenue on that day and on an average day
"""


####################
# Adjustments represent the expected multiple of difference in box office revenue for a given day tag as compared to a normal day. For example, summer week days will have positive values whereas spring week days will have negative values.
####################

tag_data = get_day_tag_data()
tag_weight_averages = tag_data.tag_weight_averages
days_since_first_friday_weight_averages = tag_data.days_since_first_friday_weight_averages
day_tags_dict = tag_data.day_tags_dict


# make a function to get the weight for each day
def get_adjustment_weight(date: dt.date) -> float:

    # if there are tags weights average those, otherwise use the days since first friday
    tags = get_day_tags(date, day_tags_dict)
    if date in day_tags_dict and len(tags) > 0:
        tag_weight = 0
        for tag in tags:
            tag_weight += tag_weight_averages[tag.value]

        return (tag_weight) / len(tags)


    days_since_first_friday = get_days_since_first_friday(date)

    return days_since_first_friday_weight_averages[days_since_first_friday]


# print the highest and lowest weights and their day

# print(
#     f"{min(days_since_first_friday_weight_averages)}: {days_since_first_friday_weight_averages.index(min(days_since_first_friday_weight_averages))}"
# )

# print(
#     f"{max(days_since_first_friday_weight_averages)}: {days_since_first_friday_weight_averages.index(max(days_since_first_friday_weight_averages))}"
# )

def plot_weights():
    import matplotlib.pyplot as plt
    from mplcursors import cursor

    plt.figure(figsize=(20, 10))

    x = list(range(len(days_since_first_friday_weight_averages)))
    y = days_since_first_friday_weight_averages

    # put a marker every 7 days
    for i in range(0, len(x), 7):
        plt.scatter(x[i], y[i], color="red")

    # plot the holiday tags for the year 2025
    current_day = dt.date(2025, 1, 1)
    while current_day.year == 2025:
        tags = get_day_tags(current_day, day_tags_dict)
        if len(tags) > 0:
            plt.scatter(
                get_days_since_first_friday(current_day),
                get_adjustment_weight(current_day),
                color="green",
            )
            # label the point with the tag name
            for tag in tags:
                plt.annotate(
                    tag.name,
                    (get_days_since_first_friday(current_day), get_adjustment_weight(current_day)),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                )
        current_day += dt.timedelta(days=1)

    plt.plot(x, y)
    plt.xlabel("Days since first Friday of the year")
    plt.ylabel("Weight")
    plt.title("Weight vs Days since first Friday of the year")
    cursor(hover=True)

    plt.show()

# plot_weights()


