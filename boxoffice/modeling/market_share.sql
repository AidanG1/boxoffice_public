DROP FUNCTION IF EXISTS market_share(TEXT, DATE, DATE);
CREATE OR REPLACE FUNCTION market_share(
    category TEXT,
    start_date DATE DEFAULT NULL,
    end_date DATE DEFAULT NULL
)
RETURNS TABLE (
    category_item TEXT,
    total_revenue NUMERIC,
    market_share NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH category_data AS (
        SELECT 
            CASE 
                WHEN category = 'numbers_genre' THEN m.genre
                WHEN category = 'tmdb_genre' THEN g.name
                WHEN category = 'mpaa' THEN m.mpaa_rating
                WHEN category = 'source' THEN m.source
                WHEN category = 'production_method' THEN m.production_method
                WHEN category = 'creative' THEN m.creative_type
                WHEN category = 'language' THEN sl.name
                WHEN category = 'country' THEN pc.name
                WHEN category = 'company' THEN pc_co.name
                ELSE NULL
            END AS category_item_value,
            SUM(bod.revenue) AS total_revenue_value
        FROM boxofficeday bod
        LEFT JOIN movie m ON bod.movie_id = m.id
        LEFT JOIN movie_genre mg ON bod.movie_id = mg.movie_id
        LEFT JOIN genre g ON mg.genre_id = g.id
        LEFT JOIN movie_spoken_language mg_sl ON bod.movie_id = mg_sl.movie_id
        LEFT JOIN spoken_language sl ON mg_sl.spoken_language_id = sl.id
        LEFT JOIN movie_production_country mpc ON bod.movie_id = mpc.movie_id
        LEFT JOIN production_country pc ON mpc.production_country_id = pc.id
        LEFT JOIN movie_production_company mpc_co ON bod.movie_id = mpc_co.movie_id
        LEFT JOIN production_company pc_co ON mpc_co.production_company_id = pc_co.id
        WHERE bod.date BETWEEN COALESCE(start_date, '2015-01-01') AND COALESCE(end_date, CURRENT_DATE)
        GROUP BY category_item_value
    ),
    total_revenue_all_cte AS (
        SELECT SUM(total_revenue_value) AS total_revenue_all
        FROM category_data
    ),
    top_categories AS (
        SELECT *
        FROM category_data
        ORDER BY total_revenue_value DESC
        LIMIT 20
    ),
    others AS (
        SELECT 'Others' AS category_item_value,
               SUM(total_revenue_value) AS total_revenue_value,
               SUM(total_revenue_value) * 1.0 / (SELECT total_revenue_all FROM total_revenue_all_cte) AS market_share_value
        FROM category_data
        WHERE category_item_value NOT IN (SELECT category_item_value FROM top_categories)
    )
    SELECT category_item_value AS category_item,
           total_revenue_value AS total_revenue,
           total_revenue_value * 1.0 / (SELECT total_revenue_all FROM total_revenue_all_cte) AS market_share_value
    FROM top_categories
    UNION ALL
    SELECT category_item_value AS category_item,
           total_revenue_value AS total_revenue,
           market_share_value
    FROM others
    ORDER BY total_revenue DESC;
END;
$$ LANGUAGE plpgsql;

-- Example Usage:
SELECT * FROM market_share('company', '2025-01-01', '2025-12-31');