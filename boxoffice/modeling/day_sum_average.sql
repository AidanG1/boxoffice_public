-- this is useful for calculating weekend grosses

DROP function day_sum_average(date, date);-- postgres function to get the

CREATE
OR REPLACE FUNCTION day_sum_average (
    start_date date,
    end_date date,
) RETURNS TABLE (
    movie_id uuid,
    title text,
    poster_path text,
    total_revenue bigint,
    average_theaters bigint,
    is_new_release boolean,
    is_estimate boolean
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id AS movie_id,
        m.title,
        m.poster_path,
        SUM(b.revenue) AS total_revenue,
        AVG(b.theaters) AS average_theaters,
        bool_or(b.is_new) AS is_estimate,
        bool_or(b.is_estimate) AS is_new_release
    FROM
        movie m
    JOIN
        boxofficeday b ON m.id = b.movie_id
    WHERE
        b.date >= start_date AND b.date <= end_date AND b.is_preview = false
    GROUP BY
        m.id, m.title, m.poster_path
    ORDER BY
        total_revenue DESC;
END;
$$ LANGUAGE plpgsql;

-- Example usage:
SELECT
    *
FROM
    day_sum_average('2025-06-20', '2025-06-22');