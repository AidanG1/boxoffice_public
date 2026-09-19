create view release_date_view as
select
    m.id as movie_id,
    m.title,
    m.release_date,
    -- need to get the year from the release date
    extract(year from cast(m.release_date as date)) as release_year,
    -- and the month
    extract(month from cast(m.release_date as date)) as release_month,
    -- and the day
    extract(day from cast(m.release_date as date)) as release_day,
    m.poster_path
    from movie m
where m.release_date is not null
order by m.release_date;
