-- function for returning counts of genre, production country, production company, spoken language, production method, source, creative type, mpaa rating

create or replace function genre_counts()
returns table (
    genre text,
    count bigint
) as $$
begin
    return query
    select
        g.name as genre,
        count(m.id) as count
    from
        movie m
    join movie_genre mg on m.id = mg.movie_id
    join genre g on mg.genre_id = g.id
    group by g.name
    order by count desc;
end;
$$ language plpgsql;

create or replace function production_country_counts()
returns table (
    country text,
    count bigint
) as $$
begin
    return query
    select
        pc.name as country,
        count(m.id) as count
    from
        movie m
    join movie_production_country mpc on m.id = mpc.movie_id
    join production_country pc on mpc.production_country_id = pc.id
    group by pc.name
    order by count desc;
end;
$$ language plpgsql;

create or replace function production_company_counts()
returns table (
    company text,
    count bigint
) as $$
begin
    return query
    select
        pc.name as company,
        count(m.id) as count
    from
        movie m
    join movie_production_company mpc on m.id = mpc.movie_id
    join production_company pc on mpc.production_company_id = pc.id
    group by pc.name
    order by count desc;
end;
$$ language plpgsql;

create or replace function spoken_language_counts()
returns table (
    language text,
    count bigint
) as $$
begin
    return query
    select
        sl.name as language,
        count(m.id) as count
    from
        movie m
    join movie_spoken_language msl on m.id = msl.movie_id
    join spoken_language sl on msl.spoken_language_id = sl.id
    group by sl.name
    order by count desc;
end;
$$ language plpgsql;

-- this one is just a count on the movie table production_method column
create or replace function production_method_counts()
returns table (
    method text,
    count bigint
) as $$
begin
    return query
    select
        production_method as method,
        count(id) as count
    from
        movie
    group by production_method
    order by count desc;
end;
$$ language plpgsql;

create or replace function source_counts()
returns table (
    source text,
    count bigint
) as $$
begin
    return query
    select
        source as source,
        count(id) as count
    from
        movie
    group by source
    order by count desc;
end;
$$ language plpgsql;

create or replace function creative_type_counts()
returns table (
    type text,
    count bigint
) as $$
begin
    return query
    select
        creative_type as type,
        count(id) as count
    from
        movie
    group by creative_type
    order by count desc;
end;
$$ language plpgsql;

create or replace function mpaa_rating_counts()
returns table (
    rating text,
    count bigint
) as $$
begin
    return query
    select
        mpaa_rating as rating,
        count(id) as count
    from
        movie
    group by mpaa_rating
    order by count desc;
end;
$$ language plpgsql;