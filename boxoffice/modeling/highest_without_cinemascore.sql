-- DROP FUNCTION highest_grossing_without_cinemascore();
CREATE
OR REPLACE FUNCTION highest_grossing_without_cinemascore () RETURNS TABLE (
    id UUID,
    title TEXT,
    release_date TEXT,
    box_office BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT movie.id, movie.title, movie.release_date, SUM(boxofficeday.revenue) as box_office
    FROM movie JOIN boxofficeday ON movie.id = boxofficeday.movie_id
    WHERE boxofficeday.is_preview = false
    AND movie.cinemascore IS NULL
    GROUP BY movie.id, movie.title, movie.release_date
    ORDER BY box_office DESC
    LIMIT 50;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM highest_grossing_without_cinemascore();