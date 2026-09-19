CREATE TABLE
    movies (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        numbers_slug TEXT NOT NULL,
        numbers_title TEXT NOT NULL,
        numbers_synopsis TEXT NOT NULL,
        -- MPAA information
        mpaa_rating TEXT NOT NULL,
        mpaa_rating_reason TEXT NOT NULL,
        mpaa_rating_date TEXT NOT NULL,
        -- Development information
        source TEXT NOT NULL,
        genre TEXT NOT NULL,
        production_method TEXT NOT NULL,
        creative_type TEXT NOT NULL,
        -- Wikipedia information
        wikipedia_key TEXT NOT NULL unique,
        wikipedia_id INT NOT NULL unique,
        -- TMDB information
        tmdb_id INT NOT NULL unique,
        backdrop_path TEXT NOT NULL,
        budget INT NOT NULL, -- numbers also has budget but using the one from TMDB
        homepage TEXT NOT NULL,
        imdb_id TEXT NOT NULL,
        original_language TEXT NOT NULL,
        overview TEXT NOT NULL,
        poster_path TEXT NOT NULL,
        release_date TEXT NOT NULL,
        revenue INT NOT NULL,
        runtime INT NOT NULL,
        tagline TEXT NOT NULL,
        title TEXT NOT NULL,
        -- HSX information
        hsx_ticker TEXT NOT NULL,
        hsx_id INT NOT NULL unique
        -- Keywords
        keywords TEXT[] NOT NULL
    );

CREATE TABLE
    collection (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        tmdb_id INT NOT NULL unique,
        name TEXT NOT NULL,
        poster_path TEXT NOT NULL,
        backdrop_path TEXT NOT NULL
    );

CREATE TABLE
    movie_collection (
        movie_id UUID NOT NULL,
        collection_id UUID NOT NULL,
        PRIMARY KEY (movie_id, collection_id),
        FOREIGN KEY (movie_id) REFERENCES movies (id),
        FOREIGN KEY (collection_id) REFERENCES collection (id)
    );

CREATE TABLE
    genres (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        tmdb_id INT NOT NULL unique,
        name TEXT NOT NULL unique
    );

CREATE TABLE
    movie_genres (
        movie_id UUID NOT NULL,
        genre_id UUID NOT NULL,
        PRIMARY KEY (movie_id, genre_id),
        FOREIGN KEY (movie_id) REFERENCES movies (id),
        FOREIGN KEY (genre_id) REFERENCES genres (id)
    );

CREATE TABLE
    production_company (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        tmdb_id INT NOT NULL unique,
        name TEXT NOT NULL unique,
        logo_path TEXT NOT NULL
    );

CREATE TABLE
    movie_production_company (
        movie_id UUID NOT NULL,
        production_company_id UUID NOT NULL,
        PRIMARY KEY (movie_id, production_company_id),
        FOREIGN KEY (movie_id) REFERENCES movies (id),
        FOREIGN KEY (production_company_id) REFERENCES production_company (id)
    );

CREATE TABLE
    production_country (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        iso_3166_1 TEXT NOT NULL unique,
        name TEXT NOT NULL unique
    );

CREATE TABLE
    movie_production_country (
        movie_id UUID NOT NULL,
        production_country_id UUID NOT NULL,
        PRIMARY KEY (movie_id, production_country_id),
        FOREIGN KEY (movie_id) REFERENCES movies (id),
        FOREIGN KEY (production_country_id) REFERENCES production_country (id)
    );

CREATE TABLE
    spoken_language (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        iso_639_1 TEXT NOT NULL unique,
        name TEXT NOT NULL unique
    );

CREATE TABLE
    movie_spoken_language (
        movie_id UUID NOT NULL,
        spoken_language_id UUID NOT NULL,
        PRIMARY KEY (movie_id, spoken_language_id),
        FOREIGN KEY (movie_id) REFERENCES movies (id),
        FOREIGN KEY (spoken_language_id) REFERENCES spoken_language (id)
    );

CREATE TABLE
    boxofficeday (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        movie_id UUID NOT NULL,
        date DATE NOT NULL,
        revenue INT NOT NULL,
        theaters INT NOT NULL,
        is_preview BOOLEAN NOT NULL,
        is_new_release BOOLEAN NOT NULL,
        FOREIGN KEY (movie_id) REFERENCES movies (id)
    );

CREATE TABLE
    -- movie info days exist for 1 month before release date and every day the movie is in theaters
    movie_info_day (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        movie_id UUID NOT NULL,
        date DATE NOT NULL,
        is_backfilled BOOLEAN NOT NULL, -- if the data was scraped 
        -- TMdB information
        tmdb_popularity FLOAT NOT NULL,
        tmdb_vote_average FLOAT NOT NULL,
        tmdb_vote_count INT NOT NULL,
        -- IMdB information
        imdb_rating FLOAT NOT NULL,
        imdb_votes INT NOT NULL,
        metacritic_rating INT, -- can be null because not all movies have a metacritic rating
        -- Wikipedia information
        wikipedia_views INT, -- can be null because some movies do not have a wikipedia page
        -- HSX information
        hsx_price FLOAT, -- can be null because some types of movies such as re-releases and special events do not have a price
        -- Trailer view information
        youtube_trailer_views INTEGER[] NOT NULL -- array of views for each trailer, top 10 results
    );

CREATE TABLE
    person (
        -- this table is created just from the appended credits and not by scraping each person
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        tmdb_id INT NOT NULL unique,
        name TEXT NOT NULL,
        profile_path TEXT NOT NULL
    );

CREATE TABLE
    castorcrew (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        tmdb_id INT NOT NULL unique,
        movie_id UUID NOT NULL,
        person_id UUID NOT NULL,
        is_cast BOOLEAN NOT NULL,
        -- Cast information
        character_name TEXT, -- null if crew
        credit_order INT, -- null if crew
        -- Crew information
        department TEXT, -- null if cast
        job TEXT, -- null if cast
        FOREIGN KEY (person_id) REFERENCES person (id),
        FOREIGN KEY (movie_id) REFERENCES movies (id)
    );

CREATE TABLE
    -- https://the-numbers.com/movies/release-schedule
    movie_release_date (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        movie_id UUID NOT NULL,
        release_date DATE NOT NULL,
        release_type TEXT NOT NULL -- many different types that the numbers uses
    );
