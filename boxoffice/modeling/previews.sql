-- sql function to get all movies with previews and then the preview vs full friday, first 3 days, first week, and total

create or replace function preview_comparison() returns table (
    return_id uuid,
    title text,
    preview_revenue bigint,
    full_friday_revenue bigint,
    first_3_days_revenue bigint,
    first_week_revenue bigint,
    total_revenue bigint
) as $$
begin
    return query
    with preview_data as (
        select
            m.id as return_id,
            m.title,
            sum(b.revenue) as preview_revenue
        from
            movie m
        join
            boxofficeday b on m.id = b.movie_id
        where
            b.is_preview = true
        group by m.id, m.title
    ),
    full_friday_data as (
        select
            m.id as return_id,
            sum(b.revenue) as full_friday_revenue
        from
            movie m
        join
            boxofficeday b on m.id = b.movie_id
        where
            b.is_preview = false and b.date = (select min(date) from boxofficeday where movie_id = m.id) + interval '1 day'
        group by m.id
    ),
    first_3_days_data as (
        select
            m.id as return_id,
            sum(b.revenue) as first_3_days_revenue
        from
            movie m
        join
            boxofficeday b on m.id = b.movie_id
        where
            b.is_preview = false and b.date >= (select min(date) from boxofficeday where movie_id = m.id) and b.date < (select min(date) from boxofficeday where movie_id = m.id) + interval '3 days'
        group by m.id
    ),
    first_week_data as (
        select
            m.id as return_id,
            sum(b.revenue) as first_week_revenue
        from
            movie m
        join
            boxofficeday b on m.id = b.movie_id
        where
            b.is_preview = false and b.date >= (select min(date) from boxofficeday where movie_id = m.id) and b.date < (select min(date) from boxofficeday where movie_id = m.id) + interval '7 days'
        group by m.id
    ),
    total_revenue_data as (
        select
            m.id as return_id,
            sum(b.revenue) as total_revenue
        from
            movie m
        join
            boxofficeday b on m.id = b.movie_id
        where
            b.is_preview = false
        group by m.id
    )
    select
        p.return_id,
        p.title,
        p.preview_revenue,
        f.full_friday_revenue,
        f3.first_3_days_revenue,
        fw.first_week_revenue,
        tr.total_revenue
    from
        preview_data p
    left join
        full_friday_data f on p.return_id = f.return_id
    left join
        first_3_days_data f3 on p.return_id = f3.return_id
    left join
        first_week_data fw on p.return_id = fw.return_id
    left join
        total_revenue_data tr on p.return_id = tr.return_id 
    where
        tr.total_revenue > 0
    order by p.preview_revenue desc;
end;
$$ language plpgsql;

select * from preview_comparison();