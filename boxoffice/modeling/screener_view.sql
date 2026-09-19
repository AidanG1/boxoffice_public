drop materialized view public.screener_view;

create materialized view
    public.screener_view as
SELECT
    m.id AS movie_id,
    m.title,
    m.release_date,
    m.budget,
    m.mpaa_rating,
    m.source,
    m.genre,
    m.production_method,
    m.creative_type,
    m.original_language,
    m.runtime,
    m.cinemascore,
    (
        SELECT
            max(mid.tmdb_popularity) AS max_tmdb_popularity
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
    ) AS max_tmdb_popularity,
    (
        SELECT
            mid.tmdb_vote_average
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS tmdb_vote_average,
    (
        SELECT
            mid.tmdb_vote_count
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS tmdb_vote_count,
    (
        SELECT
            round(mid.imdb_rating / 10.0, 2)
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS imdb_rating,
    (
        SELECT
            mid.imdb_votes
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS imdb_vote_count,
    (
        SELECT
            mid.metacritic_rating
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS metacritic_rating,
    (
        SELECT
            mid.youtube_sum_1_views
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS youtube_sum_1_views,
    (
        SELECT
            mid.youtube_sum_3_views
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS youtube_sum_3_views,
    (
        SELECT
            mid.youtube_sum_all_views
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS youtube_sum_all_views,
    (
        SELECT
            sum(bod.revenue) AS sum
        FROM
            boxofficeday bod
        WHERE
            bod.movie_id = m.id
            AND bod.is_preview = false
    ) AS domestic_revenue,
    (
        SELECT
            max(bod.revenue) AS max
        FROM
            boxofficeday bod
        WHERE
            bod.movie_id = m.id
    ) AS max_daily_revenue,
    (
        SELECT
            max(bod.theaters) AS max
        FROM
            boxofficeday bod
        WHERE
            bod.movie_id = m.id
    ) AS max_theater_count,
    (
        SELECT
            count(*) AS count
        FROM
            boxofficeday bod
        WHERE
            bod.movie_id = m.id
    ) AS days_in_theaters,
    (
        SELECT
            sum(bod.revenue) AS sum
        FROM
            boxofficeday bod
        WHERE
            bod.movie_id = m.id
            AND bod.is_preview = true
    ) AS preview_revenue,
    -- production companies
    (
        SELECT
            array_agg(pc.name) AS names
        FROM
            movie_production_company mpc
            JOIN production_company pc ON mpc.production_company_id = pc.id
        WHERE
            mpc.movie_id = m.id
    ) AS production_companies,
    -- production countries
    (
        SELECT
            array_agg(pc.name) AS names
        FROM
            movie_production_country mpc
            JOIN production_country pc ON mpc.production_country_id = pc.id
        WHERE
            mpc.movie_id = m.id
    ) AS production_countries,
    -- genres
    (
        SELECT
            array_agg(g.name) AS names
        FROM
            movie_genre mg
            JOIN genre g ON mg.genre_id = g.id
        WHERE
            mg.movie_id = m.id
    ) AS genres,
    m.collection_id is not null AS in_collection,
    -- collection name
    (
        SELECT
            c.name
        FROM
            collection c
        WHERE
            c.id = m.collection_id
    ) AS collection_name,
    -- total wikipedia views
    (
        SELECT
            sum(mid.wikipedia_views) AS total_wikipedia_views
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
    ),
    -- max wikipedia views
    (
        SELECT
            max(mid.wikipedia_views) AS max_wikipedia_views
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
    ),
    -- letterboxd listed count
    (
        SELECT
            mid.letterboxd_listed_count
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS letterboxd_listed_count,
    -- letterboxd liked count
    (
        SELECT
            mid.letterboxd_liked_count
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS letterboxd_liked_count,
    -- letterboxd rating count
    (
        SELECT
            mid.letterboxd_rating_count
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS letterboxd_rating_count,
    -- letterboxd watched count
    (
        SELECT
            mid.letterboxd_watched_count
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS letterboxd_watched_count,
    -- letterboxd average rating
    (
        SELECT
            round(mid.letterboxd_average_rating / 100.0, 2)
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS letterboxd_average_rating,
    -- rt user review count
    (
        SELECT
            mid.rt_user_review_count
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS rt_user_review_count,
    -- rt popcorn meter
    (
        SELECT
            mid.rt_popcorn_meter
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS rt_popcorn_meter,
    -- rt tomatometer
    (
        SELECT
            mid.rt_tomato_meter
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS rt_tomato_meter,
    m.poster_path,
    -- ratio of total gross to budget
    CASE
        WHEN m.budget IS NULL
        OR m.budget = 0 THEN NULL
        ELSE CASE
            WHEN (
                SELECT
                    sum(bod.revenue) AS sum
                FROM
                    boxofficeday bod
                WHERE
                    bod.movie_id = m.id
            ) IS NULL THEN NULL
            ELSE (
                SELECT
                    sum(bod.revenue)::float8 AS sum
                FROM
                    boxofficeday bod
                WHERE
                    bod.movie_id = m.id
            ) / m.budget::float8
        END
    END AS gross_to_budget_ratio,
    -- preview ratio, ratio of first day revenue minus preview revenue to preview
    (
        SELECT
            (first_day_revenue - preview_revenue) / NULLIF(preview_revenue, 0)
        FROM
            (
                SELECT
                    bod.revenue::float8 AS first_day_revenue,
                    (
                        SELECT
                            sum(bod.revenue)::float8
                        FROM
                            boxofficeday bod
                        WHERE
                            bod.movie_id = m.id
                            AND bod.is_preview = true
                    ) AS preview_revenue
                FROM
                    boxofficeday bod
                WHERE
                    bod.movie_id = m.id
                    AND bod.is_new_release = true
                LIMIT
                    1
            ) sub
    ) AS preview_ratio,
    -- opening day
    (
        SELECT
            bod.revenue::float8 AS revenue
        FROM
            boxofficeday bod
        WHERE
            bod.movie_id = m.id
            AND bod.is_new_release = true
        LIMIT
            1
    ) AS opening_day_revenue,
    -- opening day of week
    (
        SELECT
            extract(
                dow
                from
                    bod.date
            )::int AS day_of_week
        FROM
            boxofficeday bod
        WHERE
            bod.movie_id = m.id
            AND bod.is_new_release = true
        LIMIT
            1
    ) AS opening_day_of_week,
    -- opening weekend (sum of first friday, saturday, sunday)
    (
        SELECT
            sum(revenue)::float8
        FROM
            (
                SELECT
                    bod.revenue
                FROM
                    boxofficeday bod
                WHERE
                    bod.movie_id = m.id
                    AND extract(
                        dow
                        from
                            bod.date
                    ) IN (5, 6, 0)
                ORDER BY
                    bod.date ASC
                LIMIT
                    3
            ) sub
    ) AS opening_weekend_revenue,
    -- legs. Ratio of total revenue to the sum of the top 3 daily revenues
    (
        SELECT
            sum(bod.revenue)::float8
        FROM
            boxofficeday bod
        WHERE
            bod.movie_id = m.id
    ) / NULLIF(
        (
            SELECT
                sum(sub.revenue)::float8
            FROM
                (
                    SELECT
                        bod.revenue
                    FROM
                        boxofficeday bod
                    WHERE
                        bod.movie_id = m.id
                    ORDER BY
                        bod.revenue DESC
                    LIMIT
                        3
                ) sub
        ),
        0
    ) AS legs,
    -- international_box_office
    (
        SELECT
            mid.international_box_office
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS international_box_office,
    -- total box office. This should be the sum of domestic and international box office
    (
        SELECT
            sum(bod.revenue)::float8 AS domestic_box_office
        FROM
            boxofficeday bod
        WHERE
            bod.movie_id = m.id
    ) + (
        SELECT
            mid.international_box_office::float8 AS international_box_office
        FROM
            movie_info_day mid
        WHERE
            mid.movie_id = m.id
        ORDER BY
            mid.date DESC
        LIMIT
            1
    ) AS worldwide_box_office,
    -- domestic share is the percentage of domestic box office to worldwide box office
    (
        SELECT
            sum(bod.revenue)::float8 AS domestic_box_office
        FROM
            boxofficeday bod
        WHERE
            bod.movie_id = m.id
    ) / (
        (
            SELECT
                sum(bod.revenue)::float8 AS domestic_box_office
            FROM
                boxofficeday bod
            WHERE
                bod.movie_id = m.id
        ) + (
            SELECT
                mid.international_box_office::float8 AS international_box_office
            FROM
                movie_info_day mid
            WHERE
                mid.movie_id = m.id
            ORDER BY
                mid.date DESC
            LIMIT
                1
        )
    ) AS domestic_share
FROM
    movie m
ORDER BY
    m.release_date desc;

-- CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS screener_view_movie_id_idx ON public.screener_view (movie_id);
-- select
--     refresh_screener_view ();