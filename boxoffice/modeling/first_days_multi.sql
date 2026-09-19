-- take in a list of movie ids and return the first x box office days (not including previews) for each movie
-- DROP function first_days_multi (uuid[], integer);

-- take in a list of movie ids and return the first x box office days for each movie
CREATE
OR REPLACE FUNCTION first_days_multi (movie_ids uuid[], x integer) RETURNS TABLE (
    return_id uuid,
    date date,
    revenue integer
) AS $$
DECLARE
    iter_movie_id uuid;
BEGIN
    FOREACH iter_movie_id IN ARRAY movie_ids
    LOOP
        RETURN QUERY
        SELECT
            movie_id,
            b.date,
            b.revenue
        FROM
            boxofficeday as b
        WHERE
            movie_id = iter_movie_id and is_preview = false
        ORDER BY
            b.date ASC
        LIMIT x;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT
    *
FROM
    first_days_multi(
        ARRAY[
            'f28bf7a3-2097-46fe-9742-2f82c91dd317',
            '88d1658c-1f87-4c5a-91c5-ab754a142c9a'
        ]::uuid[],
        5
    );
