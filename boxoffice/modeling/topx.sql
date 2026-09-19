-- postgres function to get the top x movies by total revenue
-- Arguments:
-- 1. x: the number of movies to return

DROP function topx(integer);-- postgres function to get the

CREATE
OR REPLACE FUNCTION topx (x integer) RETURNS TABLE (
    return_id uuid,
    title text,
    total_revenue bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id AS return_id,
        m.title,
        s.total_revenue
    FROM
        movie m
    JOIN
        (
            SELECT
                movie_id,
                SUM(revenue) AS total_revenue
            FROM
                boxofficeday
            WHERE
                is_preview = false
            GROUP BY
                movie_id
        ) s
    ON
        m.id = s.movie_id
    ORDER BY
        total_revenue DESC
    LIMIT x;
END;
$$ LANGUAGE plpgsql;

select * from topx(5);