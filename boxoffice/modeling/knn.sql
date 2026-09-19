-- postgres function to calculate the knn on the movie table
-- Arguments:
-- 1. movie_id: the id of the movie to calculate the knn for
-- 2. k: the number of neighbors to consider
-- use: MPAA rating, source, genre, production_method, creative_type, budget
-- DROP function knn(uuid, integer, boolean, json);-- postgres function to calculate the knn on the movie table
-- DROP function bulk_knn(uuid[], integer, boolean);-- postgres function to calculate the knn on the movie table
-- Arguments:
-- 1. movie_id: the id of the movie to calculate the knn for
-- 2. k: the number of neighbors to consider
-- use: MPAA rating, source, genre, production_method, creative_type, budget
CREATE
OR REPLACE FUNCTION knn_inside (
    movie_id_og UUID,
    k INTEGER,
    restrict_before BOOLEAN DEFAULT FALSE,
    weights JSON DEFAULT '{"mpaa_rating": 1, "source": 1, "genre": 1, "production_method": 1, "creative_type": 1, "budget": 1, "genres": 1, "spoken_languages": 1, "production_countries": 0.5, "production_companies": 0.5, "release_dates": 4, "release_dates_count": 3}'
) RETURNS TABLE (
    return_id UUID,
    title TEXT,
    similarity NUMERIC,
    budget INTEGER
) AS $$
DECLARE
    similar_movie RECORD;
    w_mpaa_rating NUMERIC := (weights->>'mpaa_rating')::NUMERIC;
    w_source NUMERIC := (weights->>'source')::NUMERIC;
    w_genre NUMERIC := (weights->>'genre')::NUMERIC;
    w_production_method NUMERIC := (weights->>'production_method')::NUMERIC;
    w_creative_type NUMERIC := (weights->>'creative_type')::NUMERIC;
    w_budget NUMERIC := (weights->>'budget')::NUMERIC;
    w_genres NUMERIC := (weights->>'genres')::NUMERIC;
    w_spoken_languages NUMERIC := (weights->>'spoken_languages')::NUMERIC;
    w_production_countries NUMERIC := (weights->>'production_countries')::NUMERIC;
    w_production_companies NUMERIC := (weights->>'production_companies')::NUMERIC;
    w_release_dates NUMERIC := (weights->>'release_dates')::NUMERIC;
    w_release_dates_count NUMERIC := (weights->>'release_dates_count')::NUMERIC;
BEGIN
    -- Get the requested movie
    SELECT * INTO similar_movie FROM movie WHERE id = movie_id_og;

    RETURN QUERY
    WITH genre_similarity AS (
        SELECT mg.movie_id, COUNT(*) AS count
        FROM movie_genre mg
        JOIN movie_genre smg ON mg.genre_id = smg.genre_id AND smg.movie_id = similar_movie.id
        GROUP BY mg.movie_id
    ),
    spoken_language_similarity AS (
        SELECT msl.movie_id, COUNT(*) AS count
        FROM movie_spoken_language msl
        JOIN movie_spoken_language smsl ON msl.spoken_language_id = smsl.spoken_language_id AND smsl.movie_id = similar_movie.id
        GROUP BY msl.movie_id
    ),
    production_country_similarity AS (
        SELECT mc.movie_id, COUNT(*) AS count
        FROM movie_production_country mc
        JOIN movie_production_country smc ON mc.production_country_id = smc.production_country_id AND smc.movie_id = similar_movie.id
        GROUP BY mc.movie_id
    ),
    production_company_similarity AS (
        SELECT mpc.movie_id, COUNT(*) AS count
        FROM movie_production_company mpc
        JOIN movie_production_company smpc ON mpc.production_company_id = smpc.production_company_id AND smpc.movie_id = similar_movie.id
        GROUP BY mpc.movie_id
    ),
    release_date_similarity AS (
        SELECT mr.movie_id, COUNT(*) AS count
        FROM movie_release_date mr
        JOIN movie_release_date smr ON mr.release_type = smr.release_type AND smr.movie_id = similar_movie.id
        GROUP BY mr.movie_id
    ),
    release_date_count AS (
        SELECT mr.movie_id, COUNT(*) AS count
        FROM movie_release_date mr
        GROUP BY mr.movie_id
    )
    SELECT
        m.id AS return_id,
        m.title,
        (
            (CASE WHEN m.mpaa_rating = similar_movie.mpaa_rating THEN 0 ELSE 1 END) * w_mpaa_rating +
            (CASE WHEN m.source = similar_movie.source THEN 0 ELSE 1 END) * w_source +
            (CASE WHEN m.genre = similar_movie.genre THEN 0 ELSE 1 END) * w_genre +
            (CASE WHEN m.production_method = similar_movie.production_method THEN 0 ELSE 1 END) * w_production_method +
            (CASE WHEN m.creative_type = similar_movie.creative_type THEN 0 ELSE 1 END) * w_creative_type +
            (CASE WHEN (similar_movie.budget + m.budget) != 0 THEN ABS((similar_movie.budget - m.budget) / (similar_movie.budget + m.budget)) ELSE 1 END) * w_budget -
            COALESCE(gs.count, 0) * w_genres -
            COALESCE(sls.count, 0) * w_spoken_languages -
            COALESCE(pcs.count, 0) * w_production_countries -
            COALESCE(pcos.count, 0) * w_production_companies -
            COALESCE(rds.count, 0) * w_release_dates +
            COALESCE(rdc.count, 0) * w_release_dates_count
        ) AS similarity,
        m.budget
    FROM
        movie m
    LEFT JOIN genre_similarity gs ON m.id = gs.movie_id
    LEFT JOIN spoken_language_similarity sls ON m.id = sls.movie_id
    LEFT JOIN production_country_similarity pcs ON m.id = pcs.movie_id
    LEFT JOIN production_company_similarity pcos ON m.id = pcos.movie_id
    LEFT JOIN release_date_similarity rds ON m.id = rds.movie_id
    LEFT JOIN release_date_count rdc ON m.id = rdc.movie_id
    WHERE
        m.id != movie_id_og
        AND (NOT restrict_before OR m.release_date < similar_movie.release_date)
        AND EXISTS (
            SELECT 1
            FROM boxofficeday bod
            WHERE bod.movie_id = m.id
            GROUP BY bod.movie_id
            HAVING COUNT(*) >= 10
        )
        -- only movies released since 2015
        AND m.release_date >= '2015-06-01'
    ORDER BY
        similarity ASC
    LIMIT k;
END;
$$ LANGUAGE plpgsql;

CREATE
OR REPLACE FUNCTION knn (
    movie_id_og UUID,
    k INTEGER,
    restrict_before BOOLEAN DEFAULT FALSE,
    weights JSON DEFAULT '{"mpaa_rating": 1, "source": 1, "genre": 1, "production_method": 1, "creative_type": 1, "budget": 1, "genres": 1, "spoken_languages": 1, "production_countries": 0.5, "production_companies": 0.5, "release_dates": 4, "release_dates_count": 3}'
) RETURNS TABLE (
    return_id UUID,
    title TEXT,
    similarity NUMERIC,
    budget INTEGER
) AS $$
BEGIN

    -- Use a temporary table to avoid running knn_inside twice
    CREATE TEMP TABLE tmp_knn_results AS
        SELECT * FROM knn_inside(movie_id_og, k, restrict_before, weights);

    -- Remove all comps for the movie_id_og
    DELETE FROM movie_comps WHERE movie_id = movie_id_og;
    INSERT INTO movie_comps (movie_id, comp_id)
    SELECT movie_id_og, tmp_knn_results.return_id FROM tmp_knn_results;

    RETURN QUERY SELECT tmp_knn_results.return_id, tmp_knn_results.title, tmp_knn_results.similarity, tmp_knn_results.budget FROM tmp_knn_results;

    DROP TABLE tmp_knn_results;
END;
$$ LANGUAGE plpgsql;

create
or replace function bulk_knn (
    movie_ids uuid[],
    k integer,
    restrict_before boolean default false,
    weights json default '{"mpaa_rating": 1, "source": 1, "genre": 1, "production_method": 1, "creative_type": 1, "budget": 4, "genres": 1, "spoken_languages": 1, "production_countries": 0.5, "production_companies": 0.5, "release_dates": 4, "release_dates_count": 3}'
) RETURNS table (
    return_id uuid,
    title text,
    similarity numeric,
    budget integer,
    similar_id uuid
) as $$
-- loop through the movie ids and run the knn function for each
DECLARE
    movie_id uuid;
BEGIN
    -- loop through the movie ids
    FOREACH movie_id IN ARRAY movie_ids LOOP
    -- get the requested movie
    RETURN QUERY EXECUTE 'SELECT return_id, title, similarity, budget, $1 as similar_id FROM knn($1, $2, $3, $4)' USING movie_id, k, restrict_before, weights;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

select
    *
from
    knn ('3e885c07-01c6-4b77-a37c-70451eef1cf6', 10, true);

select
    *
from
    bulk_knn (
        ARRAY[
            uuid('3e885c07-01c6-4b77-a37c-70451eef1cf6'),
            uuid('58c0cc1e-76b0-473d-8622-b778cf679cb7')
        ],
        10,
        true
-- run knn on movies with ids 100 through 200 (assuming sequential ids)
SELECT
    knn(
        movie.id,
        8,
        true
    )
FROM
    movie
WHERE
    id IN (
        SELECT id FROM movie ORDER BY id OFFSET 100 LIMIT 100
    );
