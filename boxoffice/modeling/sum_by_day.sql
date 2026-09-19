-- sql function that returns the sum by day of all box office days within a range
-- DROP function sum_by_day (date, date);

CREATE
OR REPLACE FUNCTION sum_by_day (start_date date, end_date date, filter_x_days integer) RETURNS TABLE (
    date date,
    revenue bigint,
    theater_count bigint,
    budget_sum bigint,
    theater_weighted_budget bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        b.date,
        SUM(b.revenue) AS revenue,
        SUM(b.theaters) AS theater_count,
        SUM(m.budget) AS budget_sum,
        SUM(m.budget / 1000000 * b.theaters) AS theater_weighted_budget
    FROM
        boxofficeday b
    JOIN
        movie m
    ON
        b.movie_id = m.id
    WHERE
        b.date >= start_date AND
        b.date <= end_date AND
        b.is_preview is false AND
        b.date > (
            SELECT MIN(b2.date)
            FROM boxofficeday b2
            WHERE b2.movie_id = b.movie_id
            GROUP BY b2.movie_id
            LIMIT 1
        ) + filter_x_days
    GROUP BY
        b.date
    ORDER BY
        b.date ASC;
END;
$$ LANGUAGE plpgsql;

SELECT
    *
FROM
    sum_by_day ('2016-01-01', '2016-01-31', 5)