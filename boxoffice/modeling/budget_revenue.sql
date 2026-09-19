drop function get_budget_revenue();

-- function to get the budget and revenue for every movie
CREATE OR REPLACE FUNCTION get_budget_revenue()
RETURNS TABLE (
    movie_id uuid,
    budget integer,
    revenue bigint,
    collection_id uuid
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id AS movie_id,
        m.budget AS budget,
        sum(bod.revenue) AS revenue,
        m.collection_id AS collection_id
    FROM
        movie m
    LEFT JOIN boxofficeday bod ON m.id = bod.movie_id
    GROUP BY
        m.id
    ORDER BY
        m.id;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM get_budget_revenue();

-- function to get the quartiles for daily gross
CREATE OR REPLACE FUNCTION get_daily_quartiles()
RETURNS TABLE (
    movie_id uuid,
    min integer,
    q1 double precision,
    q2 double precision,
    q3 double precision,
    max integer
) AS $$

BEGIN
    RETURN QUERY
    SELECT
        m.id AS movie_id,
        min(bod.revenue) AS min,
        percentile_cont(0.25) WITHIN GROUP (ORDER BY bod.revenue) AS q1,
        percentile_cont(0.5) WITHIN GROUP (ORDER BY bod.revenue) AS q2,
        percentile_cont(0.75) WITHIN GROUP (ORDER BY bod.revenue) AS q3,
        max(bod.revenue) AS max
    FROM
        movie m
    LEFT JOIN boxofficeday bod ON m.id = bod.movie_id
    GROUP BY
        m.id
    ORDER BY
        m.id;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM get_daily_quartiles();