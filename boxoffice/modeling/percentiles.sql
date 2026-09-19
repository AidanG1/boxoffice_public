-- rpc function that takes in a movie_id and gets the percentiles for that movie using screener_view
-- it should return a table with a column for category and a column for the percentile value
-- the categories are budget, runtime, tmdb_vote_average, tmdb_vote_count, imdb_rating, imdb_vote_count, metacritic_rating, youtube_sum_all_views, total_revenue, max_daily_revenue, max_theater_count, days_in_theaters, total_wikipedia_views, max_wikipedia_views, letterboxd_rating_count, letterboxd_average_rating, rt_user_review_count, rt_popcorn_meter, rt_tomato_meter, opening_day_revenue, gross_to_budget_ratio, opening_weekend_revenue, legs, preview_ratio

-- DROP FUNCTION IF EXISTS percent_ranks(uuid);

CREATE OR REPLACE FUNCTION percent_ranks(input_id uuid)
RETURNS TABLE (
    category TEXT,
    percent_rank FLOAT,
    value FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM (
        SELECT 'budget' AS category, p_rank, budget AS value FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY budget) AS p_rank, budget FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'runtime', p_rank, runtime FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY runtime) AS p_rank, runtime FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'tmdb_vote_average', p_rank, tmdb_vote_average FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY tmdb_vote_average) AS p_rank, tmdb_vote_average FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'tmdb_vote_count', p_rank, tmdb_vote_count FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY tmdb_vote_count) AS p_rank, tmdb_vote_count FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'imdb_rating', p_rank, imdb_rating FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY imdb_rating) AS p_rank, imdb_rating FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'imdb_vote_count', p_rank, imdb_vote_count FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY imdb_vote_count) AS p_rank, imdb_vote_count FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'metacritic_rating', p_rank, metacritic_rating FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY metacritic_rating) AS p_rank, metacritic_rating FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'youtube_sum_all_views', p_rank, youtube_sum_all_views FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY youtube_sum_all_views) AS p_rank, youtube_sum_all_views FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'domestic_revenue', p_rank, domestic_revenue FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY domestic_revenue) AS p_rank, domestic_revenue FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'international_box_office', p_rank, international_box_office FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY international_box_office) AS p_rank, international_box_office FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'worldwide_box_office', p_rank, worldwide_box_office FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY worldwide_box_office) AS p_rank, worldwide_box_office FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'max_daily_revenue', p_rank, max_daily_revenue FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY max_daily_revenue) AS p_rank, max_daily_revenue FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'max_theater_count', p_rank, max_theater_count FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY max_theater_count) AS p_rank, max_theater_count FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'days_in_theaters', p_rank, days_in_theaters FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY days_in_theaters) AS p_rank, days_in_theaters FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'total_wikipedia_views', p_rank, total_wikipedia_views FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY total_wikipedia_views) AS p_rank, total_wikipedia_views FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'max_wikipedia_views', p_rank, max_wikipedia_views FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY max_wikipedia_views) AS p_rank, max_wikipedia_views FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'letterboxd_rating_count', p_rank, letterboxd_rating_count FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY letterboxd_rating_count) AS p_rank, letterboxd_rating_count FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'letterboxd_average_rating', p_rank, letterboxd_average_rating FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY letterboxd_average_rating) AS p_rank, letterboxd_average_rating FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'rt_user_review_count', p_rank, rt_user_review_count FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY rt_user_review_count) AS p_rank, rt_user_review_count FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'rt_popcorn_meter', p_rank, rt_popcorn_meter FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY rt_popcorn_meter) AS p_rank, rt_popcorn_meter FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'rt_tomato_meter', p_rank, rt_tomato_meter FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY rt_tomato_meter) AS p_rank, rt_tomato_meter FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'opening_day_revenue', p_rank, opening_day_revenue FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY opening_day_revenue) AS p_rank, opening_day_revenue FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'gross_to_budget_ratio', p_rank, gross_to_budget_ratio FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY gross_to_budget_ratio) AS p_rank, gross_to_budget_ratio FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'opening_weekend_revenue', p_rank, opening_weekend_revenue FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY opening_weekend_revenue) AS p_rank, opening_weekend_revenue FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'legs', p_rank, legs FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY legs) AS p_rank, legs FROM screener_view
        ) ranked WHERE movie_id = input_id
        UNION ALL
        SELECT 'preview_ratio', p_rank, preview_ratio FROM (
            SELECT movie_id, PERCENT_RANK() OVER (ORDER BY preview_ratio) AS p_rank, preview_ratio FROM screener_view
        ) ranked WHERE movie_id = input_id
    ) all_ranks;
END $$ LANGUAGE plpgsql;

-- example usage:
SELECT * FROM percent_ranks('9fcad6b4-02c8-48af-8207-a9cd9e113884');
