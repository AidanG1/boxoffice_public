-- function that takes in a movie_id and gets the weekend grosses for that movie
-- DROP FUNCTION IF EXISTS movie_weekends(movie_id uuid);
CREATE
OR REPLACE FUNCTION movie_weekends (input_id uuid) RETURNS TABLE (
    weekend_num integer,
    weekend_start_date date,
    return_id uuid,
    weekend_revenue bigint,
    weekend_theaters integer,
    is_estimate boolean,
    is_new_release boolean
) AS $$
BEGIN
    RETURN QUERY
    WITH first_fri AS (
        SELECT MIN(date) AS first_friday
        FROM boxofficeday
        WHERE movie_id = input_id
          AND EXTRACT(DOW FROM date) = 5 -- 5 = Friday
    ),
    weekend_days AS (
        SELECT
            bod.*,
            FLOOR(
                (date - (SELECT first_friday FROM first_fri)) / 7
            ) AS weekend_num
        FROM boxofficeday bod
        WHERE bod.movie_id = input_id
          AND date >= (SELECT first_friday FROM first_fri)
          AND EXTRACT(DOW FROM date) IN (5,6,0) -- Friday, Saturday, Sunday
    )
    SELECT
        weekend_days.weekend_num::integer AS weekend_num,
        MIN(date) AS weekend_start_date,
        input_id,
        SUM(revenue) AS weekend_revenue,
        AVG(theaters)::integer AS weekend_theaters,
        BOOL_OR(weekend_days.is_estimate) AS is_estimate,
        BOOL_OR(weekend_days.is_new_release) AS is_new_release
    FROM weekend_days
    GROUP BY weekend_days.weekend_num
    ORDER BY weekend_start_date;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION movie_weekends (uuid) IS 'Returns weekend grosses for a given movie_id, including start date, revenue, theater count, and flags for estimates and new releases.';

-- example
SELECT
    *
FROM
    movie_weekends ('a55a773f-7758-4186-8b85-33a1bbf668eb');