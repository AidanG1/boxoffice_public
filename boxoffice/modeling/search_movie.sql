-- search movie function

-- DROP function search_movies(text, integer);

CREATE OR REPLACE FUNCTION search_movies(search_term text, limit_count integer)
RETURNS TABLE (
    id uuid,
    title text,
    release_date text,
    distance integer
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.title,
        m.release_date,
        LEVENSHTEIN(LOWER(search_term), LOWER(m.title), 1, 50, 30) AS distance
    FROM
        movie m
    ORDER BY
        distance
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Example usage:
-- SELECT * FROM search_movies('moana 2.0 2025', 10);
SELECT * FROM search_movies('the day the', 10);