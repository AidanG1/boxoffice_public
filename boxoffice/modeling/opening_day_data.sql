-- sql function to get data necessary to train opening day model
-- This function will return a table with the following columns:
-- 1. movie_id
-- 2. movie release date
-- 3. movie genre
-- 4. movie production method
-- 5. budget
-- 6. opening day revenue (non-preview day)
-- 7. in_franchise
-- 8. pre_release_cumulative_wikipedia_views
-- 9. day_before_wikipedia_views
-- 10. day_before_imdb_rating
-- 11. day_before_youtube_views
-- drop function opening_day_data();
CREATE OR REPLACE FUNCTION opening_day_data() RETURNS TABLE (
    movie_id uuid,
    title text,
    opening_date date,
    genre text,
    production_method text,
    budget integer,
    opening_day_revenue integer,
    in_franchise boolean,
    pre_release_cumulative_wikipedia_views bigint,
    day_before_wikipedia_views integer,
    day_before_imdb_rating smallint,
    day_before_youtube_sum_1_views bigint,
    day_before_youtube_sum_3_views bigint,
    day_before_youtube_sum_all_views bigint
) AS $$
BEGIN
    RETURN QUERY
    WITH movie_opening_dates AS (
        SELECT
            m.id,
            m.title,
            m.genre,
            m.production_method,
            m.budget,
            m.collection_id,
            (
                SELECT
                    b.date
                FROM
                    boxofficeday as b
                WHERE
                    b.movie_id = m.id AND b.is_preview = false
                ORDER BY 
                    b.date ASC
                LIMIT 1
            ) AS opening_date,
            (
                SELECT
                    b.revenue
                FROM
                    boxofficeday as b
                WHERE
                    b.movie_id = m.id AND b.is_preview = false
                ORDER BY 
                    b.date ASC
                LIMIT 1
            ) AS opening_day_revenue
        FROM
            movie as m
    )
    SELECT
        mod.id,
        mod.title,
        mod.opening_date,
        mod.genre,
        mod.production_method,
        mod.budget,
        mod.opening_day_revenue,
        mod.collection_id IS NOT NULL,
        (
            SELECT
                SUM(wikipedia_views)
            FROM
                movie_info_day as mid
            WHERE
                mid.movie_id = mod.id
                AND mid.date < mod.opening_date
        ) as pre_release_cumulative_wikipedia_views,
        (
            SELECT
                mid.wikipedia_views
            FROM
                movie_info_day as mid
            WHERE
                mid.movie_id = mod.id
                AND mid.date = mod.opening_date - interval '1 day'
        ) AS day_before_wikipedia_views,
        (
            SELECT
                mid.imdb_rating
            FROM
                movie_info_day as mid
            WHERE
                mid.movie_id = mod.id
                AND mid.date = mod.opening_date - interval '1 day'
        ) AS day_before_imdb_rating,
        (
            SELECT
                mid.youtube_sum_1_views
            FROM
                movie_info_day as mid
            WHERE
                mid.movie_id = mod.id
                AND mid.date = mod.opening_date - interval '1 day'
        ) AS day_before_youtube_sum_1_views,
        (
            SELECT
                mid.youtube_sum_3_views
            FROM
                movie_info_day as mid
            WHERE
                mid.movie_id = mod.id
                AND mid.date = mod.opening_date - interval '1 day'
        ) AS day_before_youtube_sum_3_views,
        (
            SELECT
                mid.youtube_sum_all_views
            FROM
                movie_info_day as mid
            WHERE
                mid.movie_id = mod.id
                AND mid.date = mod.opening_date - interval '1 day'
        ) AS day_before_youtube_sum_all_views
    FROM
        movie_opening_dates mod;
END;
$$ LANGUAGE plpgsql;

SELECT
    *
from
    opening_day_data();