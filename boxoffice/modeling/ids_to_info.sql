-- takes in a list of movie ids and returns a bunch of information about them
-- drop function ids_to_info(text[]);
create
or replace function ids_to_info (ids text[]) returns table (
    return_id uuid,
    title text,
    total_revenue bigint,
    budget integer,
    release_date text,
    poster_path text
) as $$
begin
    return query select
        m.id as return_id,
        m.title,
        sum(bod.revenue) as total_revenue,
        m.budget,
        m.release_date,
        m.poster_path
    from movie m
    left join boxofficeday bod on m.id = bod.movie_id
    where m.id = any(ids::uuid[])
    group by m.id, m.title, m.budget, m.release_date, m.poster_path
    having sum(bod.revenue) > 0
    order by total_revenue desc
    limit 50;
end;
$$ language plpgsql;

-- Example usage:
select * from ids_to_info(
    array['b4526694-5c6c-44c4-9f3f-bd7b5b2cc815', '0d0d0f10-a527-47b2-8e75-8b6de0f65ba8']
);