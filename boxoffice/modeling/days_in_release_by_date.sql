-- postgres function that takes in a date, and then returns boxofficeday_id, movie_id, days_in_release
-- DROP FUNCTION days_in_release_by_date(date);
CREATE
OR REPLACE FUNCTION days_in_release_by_date (bod_date date) RETURNS TABLE (
    boxofficeday_id uuid,
    movie_id uuid,
    days_in_release int
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        b.id,
        b.movie_id,
        COUNT(*) OVER (
            PARTITION BY b.movie_id
            ORDER BY b.date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )
    FROM
        boxofficeday b
    WHERE
        b.date <= bod_date;
END;
$$ LANGUAGE plpgsql;

-- Example usage:
SELECT * FROM days_in_release_by_date('2025-06-25');