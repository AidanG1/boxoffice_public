export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "12.2.3 (519615d)"
  }
  public: {
    Tables: {
      boxofficeday: {
        Row: {
          created_at: string
          date: string
          double_day: boolean
          id: string
          is_estimate: boolean
          is_new_release: boolean
          is_preview: boolean
          movie_id: string
          revenue: number
          theaters: number | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          date: string
          double_day?: boolean
          id?: string
          is_estimate: boolean
          is_new_release: boolean
          is_preview: boolean
          movie_id: string
          revenue: number
          theaters?: number | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          date?: string
          double_day?: boolean
          id?: string
          is_estimate?: boolean
          is_new_release?: boolean
          is_preview?: boolean
          movie_id?: string
          revenue?: number
          theaters?: number | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "boxofficeday_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "movie"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "boxofficeday_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "release_date_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "boxofficeday_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "screener_view"
            referencedColumns: ["movie_id"]
          },
        ]
      }
      castorcrew: {
        Row: {
          character_name: string | null
          credit_order: number | null
          department: string | null
          id: string
          is_cast: boolean
          job: string | null
          movie_id: string
          person_id: string
        }
        Insert: {
          character_name?: string | null
          credit_order?: number | null
          department?: string | null
          id?: string
          is_cast: boolean
          job?: string | null
          movie_id: string
          person_id: string
        }
        Update: {
          character_name?: string | null
          credit_order?: number | null
          department?: string | null
          id?: string
          is_cast?: boolean
          job?: string | null
          movie_id?: string
          person_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "castorcrew_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "movie"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "castorcrew_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "release_date_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "castorcrew_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "screener_view"
            referencedColumns: ["movie_id"]
          },
          {
            foreignKeyName: "castorcrew_person_id_fkey"
            columns: ["person_id"]
            isOneToOne: false
            referencedRelation: "person"
            referencedColumns: ["id"]
          },
        ]
      }
      collection: {
        Row: {
          backdrop_path: string | null
          id: string
          name: string
          poster_path: string | null
          tmdb_id: number
        }
        Insert: {
          backdrop_path?: string | null
          id?: string
          name: string
          poster_path?: string | null
          tmdb_id: number
        }
        Update: {
          backdrop_path?: string | null
          id?: string
          name?: string
          poster_path?: string | null
          tmdb_id?: number
        }
        Relationships: []
      }
      genre: {
        Row: {
          id: string
          name: string
          tmdb_id: number
        }
        Insert: {
          id?: string
          name: string
          tmdb_id: number
        }
        Update: {
          id?: string
          name?: string
          tmdb_id?: number
        }
        Relationships: []
      }
      movie: {
        Row: {
          backdrop_path: string | null
          budget: number | null
          cinemascore: string | null
          collection_id: string | null
          created_at: string
          creative_type: string
          fandango_slug: string | null
          genre: string
          homepage: string | null
          hsx_id: number | null
          hsx_ticker: string | null
          id: string
          imdb_id: string
          keywords: string[] | null
          letterboxd_id: string | null
          mpaa_rating: string
          mpaa_rating_date: string | null
          mpaa_rating_reason: string
          numbers_slug: string
          numbers_synopsis: string | null
          numbers_title: string
          original_language: string
          overview: string
          poster_path: string | null
          production_method: string
          release_date: string
          rotten_tomatoes_id: string | null
          runtime: number
          source: string
          tagline: string | null
          title: string
          tmdb_id: number
          updated_at: string
          wikidata_id: string | null
          wikipedia_id: number | null
          wikipedia_key: string | null
        }
        Insert: {
          backdrop_path?: string | null
          budget?: number | null
          cinemascore?: string | null
          collection_id?: string | null
          created_at?: string
          creative_type: string
          fandango_slug?: string | null
          genre: string
          homepage?: string | null
          hsx_id?: number | null
          hsx_ticker?: string | null
          id?: string
          imdb_id: string
          keywords?: string[] | null
          letterboxd_id?: string | null
          mpaa_rating: string
          mpaa_rating_date?: string | null
          mpaa_rating_reason: string
          numbers_slug: string
          numbers_synopsis?: string | null
          numbers_title: string
          original_language: string
          overview: string
          poster_path?: string | null
          production_method: string
          release_date: string
          rotten_tomatoes_id?: string | null
          runtime: number
          source: string
          tagline?: string | null
          title: string
          tmdb_id: number
          updated_at?: string
          wikidata_id?: string | null
          wikipedia_id?: number | null
          wikipedia_key?: string | null
        }
        Update: {
          backdrop_path?: string | null
          budget?: number | null
          cinemascore?: string | null
          collection_id?: string | null
          created_at?: string
          creative_type?: string
          fandango_slug?: string | null
          genre?: string
          homepage?: string | null
          hsx_id?: number | null
          hsx_ticker?: string | null
          id?: string
          imdb_id?: string
          keywords?: string[] | null
          letterboxd_id?: string | null
          mpaa_rating?: string
          mpaa_rating_date?: string | null
          mpaa_rating_reason?: string
          numbers_slug?: string
          numbers_synopsis?: string | null
          numbers_title?: string
          original_language?: string
          overview?: string
          poster_path?: string | null
          production_method?: string
          release_date?: string
          rotten_tomatoes_id?: string | null
          runtime?: number
          source?: string
          tagline?: string | null
          title?: string
          tmdb_id?: number
          updated_at?: string
          wikidata_id?: string | null
          wikipedia_id?: number | null
          wikipedia_key?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "movie_collection_id_fkey"
            columns: ["collection_id"]
            isOneToOne: false
            referencedRelation: "collection"
            referencedColumns: ["id"]
          },
        ]
      }
      movie_comps: {
        Row: {
          comp_id: string
          id: string
          movie_id: string
        }
        Insert: {
          comp_id: string
          id?: string
          movie_id: string
        }
        Update: {
          comp_id?: string
          id?: string
          movie_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "movie_comps_comp_id_fkey"
            columns: ["comp_id"]
            isOneToOne: false
            referencedRelation: "movie"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_comps_comp_id_fkey"
            columns: ["comp_id"]
            isOneToOne: false
            referencedRelation: "release_date_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_comps_comp_id_fkey"
            columns: ["comp_id"]
            isOneToOne: false
            referencedRelation: "screener_view"
            referencedColumns: ["movie_id"]
          },
          {
            foreignKeyName: "movie_comps_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "movie"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_comps_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "release_date_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_comps_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "screener_view"
            referencedColumns: ["movie_id"]
          },
        ]
      }
      movie_genre: {
        Row: {
          genre_id: string
          movie_id: string
        }
        Insert: {
          genre_id: string
          movie_id: string
        }
        Update: {
          genre_id?: string
          movie_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "movie_genre_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "movie"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_genre_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "release_date_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_genre_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "screener_view"
            referencedColumns: ["movie_id"]
          },
          {
            foreignKeyName: "movie_genres_genre_id_fkey"
            columns: ["genre_id"]
            isOneToOne: false
            referencedRelation: "genre"
            referencedColumns: ["id"]
          },
        ]
      }
      movie_info_day: {
        Row: {
          created_at: string
          date: string
          hsx_price: number | null
          id: string
          imdb_rating: number
          imdb_votes: number
          international_box_office: number | null
          is_backfilled: boolean
          letterboxd_average_rating: number | null
          letterboxd_liked_count: number | null
          letterboxd_listed_count: number | null
          letterboxd_per_each_rating_counts: number[] | null
          letterboxd_rating_count: number | null
          letterboxd_watched_count: number | null
          metacritic_rating: number | null
          movie_id: string
          rt_critic_average_score: number | null
          rt_critic_review_count: number | null
          rt_popcorn_meter: number | null
          rt_tomato_meter: number | null
          rt_user_average_score: number | null
          rt_user_rating_count: number | null
          rt_user_review_count: number | null
          rt_want_to_see_count: number | null
          tmdb_popularity: number
          tmdb_vote_average: number
          tmdb_vote_count: number
          updated_at: string
          wikipedia_views: number | null
          youtube_sum_1_views: number
          youtube_sum_3_views: number
          youtube_sum_all_views: number
        }
        Insert: {
          created_at?: string
          date: string
          hsx_price?: number | null
          id?: string
          imdb_rating: number
          imdb_votes: number
          international_box_office?: number | null
          is_backfilled: boolean
          letterboxd_average_rating?: number | null
          letterboxd_liked_count?: number | null
          letterboxd_listed_count?: number | null
          letterboxd_per_each_rating_counts?: number[] | null
          letterboxd_rating_count?: number | null
          letterboxd_watched_count?: number | null
          metacritic_rating?: number | null
          movie_id: string
          rt_critic_average_score?: number | null
          rt_critic_review_count?: number | null
          rt_popcorn_meter?: number | null
          rt_tomato_meter?: number | null
          rt_user_average_score?: number | null
          rt_user_rating_count?: number | null
          rt_user_review_count?: number | null
          rt_want_to_see_count?: number | null
          tmdb_popularity: number
          tmdb_vote_average: number
          tmdb_vote_count: number
          updated_at?: string
          wikipedia_views?: number | null
          youtube_sum_1_views: number
          youtube_sum_3_views: number
          youtube_sum_all_views: number
        }
        Update: {
          created_at?: string
          date?: string
          hsx_price?: number | null
          id?: string
          imdb_rating?: number
          imdb_votes?: number
          international_box_office?: number | null
          is_backfilled?: boolean
          letterboxd_average_rating?: number | null
          letterboxd_liked_count?: number | null
          letterboxd_listed_count?: number | null
          letterboxd_per_each_rating_counts?: number[] | null
          letterboxd_rating_count?: number | null
          letterboxd_watched_count?: number | null
          metacritic_rating?: number | null
          movie_id?: string
          rt_critic_average_score?: number | null
          rt_critic_review_count?: number | null
          rt_popcorn_meter?: number | null
          rt_tomato_meter?: number | null
          rt_user_average_score?: number | null
          rt_user_rating_count?: number | null
          rt_user_review_count?: number | null
          rt_want_to_see_count?: number | null
          tmdb_popularity?: number
          tmdb_vote_average?: number
          tmdb_vote_count?: number
          updated_at?: string
          wikipedia_views?: number | null
          youtube_sum_1_views?: number
          youtube_sum_3_views?: number
          youtube_sum_all_views?: number
        }
        Relationships: [
          {
            foreignKeyName: "movie_info_day_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "movie"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_info_day_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "release_date_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_info_day_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "screener_view"
            referencedColumns: ["movie_id"]
          },
        ]
      }
      movie_prediction: {
        Row: {
          created_at: string
          id: string
          made_on_date: string
          movie_id: string | null
          predictions: number[]
          start_date: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          id?: string
          made_on_date: string
          movie_id?: string | null
          predictions: number[]
          start_date: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          id?: string
          made_on_date?: string
          movie_id?: string | null
          predictions?: number[]
          start_date?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "movie_prediction_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "movie"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_prediction_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "release_date_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_prediction_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "screener_view"
            referencedColumns: ["movie_id"]
          },
        ]
      }
      movie_production_company: {
        Row: {
          movie_id: string
          production_company_id: string
        }
        Insert: {
          movie_id: string
          production_company_id: string
        }
        Update: {
          movie_id?: string
          production_company_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "movie_production_company_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "movie"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_production_company_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "release_date_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_production_company_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "screener_view"
            referencedColumns: ["movie_id"]
          },
          {
            foreignKeyName: "movie_production_company_production_company_id_fkey"
            columns: ["production_company_id"]
            isOneToOne: false
            referencedRelation: "production_company"
            referencedColumns: ["id"]
          },
        ]
      }
      movie_production_country: {
        Row: {
          movie_id: string
          production_country_id: string
        }
        Insert: {
          movie_id: string
          production_country_id: string
        }
        Update: {
          movie_id?: string
          production_country_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "movie_production_country_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "movie"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_production_country_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "release_date_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_production_country_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "screener_view"
            referencedColumns: ["movie_id"]
          },
          {
            foreignKeyName: "movie_production_country_production_country_id_fkey"
            columns: ["production_country_id"]
            isOneToOne: false
            referencedRelation: "production_country"
            referencedColumns: ["id"]
          },
        ]
      }
      movie_release_date: {
        Row: {
          created_at: string
          id: string
          movie_id: string
          release_date: string
          release_type: string
        }
        Insert: {
          created_at?: string
          id?: string
          movie_id: string
          release_date: string
          release_type: string
        }
        Update: {
          created_at?: string
          id?: string
          movie_id?: string
          release_date?: string
          release_type?: string
        }
        Relationships: [
          {
            foreignKeyName: "movie_release_date_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "movie"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_release_date_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "release_date_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_release_date_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "screener_view"
            referencedColumns: ["movie_id"]
          },
        ]
      }
      movie_spoken_language: {
        Row: {
          movie_id: string
          spoken_language_id: string
        }
        Insert: {
          movie_id: string
          spoken_language_id: string
        }
        Update: {
          movie_id?: string
          spoken_language_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "movie_spoken_language_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "movie"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_spoken_language_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "release_date_view"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "movie_spoken_language_movie_id_fkey"
            columns: ["movie_id"]
            isOneToOne: false
            referencedRelation: "screener_view"
            referencedColumns: ["movie_id"]
          },
          {
            foreignKeyName: "movie_spoken_language_spoken_language_id_fkey"
            columns: ["spoken_language_id"]
            isOneToOne: false
            referencedRelation: "spoken_language"
            referencedColumns: ["id"]
          },
        ]
      }
      person: {
        Row: {
          id: string
          name: string
          profile_path: string | null
          tmdb_id: number
        }
        Insert: {
          id?: string
          name: string
          profile_path?: string | null
          tmdb_id: number
        }
        Update: {
          id?: string
          name?: string
          profile_path?: string | null
          tmdb_id?: number
        }
        Relationships: []
      }
      production_company: {
        Row: {
          id: string
          logo_path: string | null
          name: string
          tmdb_id: number
        }
        Insert: {
          id?: string
          logo_path?: string | null
          name: string
          tmdb_id: number
        }
        Update: {
          id?: string
          logo_path?: string | null
          name?: string
          tmdb_id?: number
        }
        Relationships: []
      }
      production_country: {
        Row: {
          id: string
          iso_3166_1: string
          name: string
        }
        Insert: {
          id?: string
          iso_3166_1: string
          name: string
        }
        Update: {
          id?: string
          iso_3166_1?: string
          name?: string
        }
        Relationships: []
      }
      spoken_language: {
        Row: {
          id: string
          iso_639_1: string
          name: string
        }
        Insert: {
          id?: string
          iso_639_1: string
          name: string
        }
        Update: {
          id?: string
          iso_639_1?: string
          name?: string
        }
        Relationships: []
      }
    }
    Views: {
      release_date_view: {
        Row: {
          id: string | null
          poster_path: string | null
          release_date: string | null
          release_day: number | null
          release_month: number | null
          release_year: number | null
          title: string | null
        }
        Insert: {
          id?: string | null
          poster_path?: string | null
          release_date?: string | null
          release_day?: never
          release_month?: never
          release_year?: never
          title?: string | null
        }
        Update: {
          id?: string | null
          poster_path?: string | null
          release_date?: string | null
          release_day?: never
          release_month?: never
          release_year?: never
          title?: string | null
        }
        Relationships: []
      }
      screener_view: {
        Row: {
          budget: number | null
          cinemascore: string | null
          collection_name: string | null
          creative_type: string | null
          days_in_theaters: number | null
          domestic_revenue: number | null
          domestic_share: number | null
          genre: string | null
          genres: string[] | null
          gross_to_budget_ratio: number | null
          imdb_rating: number | null
          imdb_vote_count: number | null
          in_collection: boolean | null
          international_box_office: number | null
          legs: number | null
          letterboxd_average_rating: number | null
          letterboxd_liked_count: number | null
          letterboxd_listed_count: number | null
          letterboxd_rating_count: number | null
          letterboxd_watched_count: number | null
          max_daily_revenue: number | null
          max_theater_count: number | null
          max_tmdb_popularity: number | null
          max_wikipedia_views: number | null
          metacritic_rating: number | null
          movie_id: string | null
          mpaa_rating: string | null
          opening_day_of_week: number | null
          opening_day_revenue: number | null
          opening_weekend_revenue: number | null
          original_language: string | null
          poster_path: string | null
          preview_ratio: number | null
          preview_revenue: number | null
          production_companies: string[] | null
          production_countries: string[] | null
          production_method: string | null
          release_date: string | null
          rt_popcorn_meter: number | null
          rt_tomato_meter: number | null
          rt_user_review_count: number | null
          runtime: number | null
          source: string | null
          title: string | null
          tmdb_vote_average: number | null
          tmdb_vote_count: number | null
          total_wikipedia_views: number | null
          worldwide_box_office: number | null
          youtube_sum_1_views: number | null
          youtube_sum_3_views: number | null
          youtube_sum_all_views: number | null
        }
        Relationships: []
      }
    }
    Functions: {
      bulk_knn: {
        Args: {
          k: number
          movie_ids: string[]
          restrict_before?: boolean
          weights?: Json
        }
        Returns: {
          budget: number
          return_id: string
          similar_id: string
          similarity: number
          title: string
        }[]
      }
      creative_type_counts: {
        Args: Record<PropertyKey, never>
        Returns: {
          count: number
          type: string
        }[]
      }
      day_sum_average: {
        Args: { end_date: string; start_date: string }
        Returns: {
          average_theaters: number
          is_estimate: boolean
          is_new_release: boolean
          movie_id: string
          poster_path: string
          title: string
          total_revenue: number
        }[]
      }
      days_in_release_by_date: {
        Args: { input_date: string }
        Returns: {
          boxofficeday_id: string
          date: string
          days_in_release: number
          movie_id: string
        }[]
      }
      first_days_multi: {
        Args: { movie_ids: string[]; x: number }
        Returns: {
          date: string
          return_id: string
          revenue: number
        }[]
      }
      genre_counts: {
        Args: Record<PropertyKey, never>
        Returns: {
          count: number
          genre: string
        }[]
      }
      get_budget_revenue: {
        Args: Record<PropertyKey, never>
        Returns: {
          budget: number
          collection_id: string
          movie_id: string
          revenue: number
        }[]
      }
      get_daily_quartiles: {
        Args: Record<PropertyKey, never>
        Returns: {
          max: number
          min: number
          movie_id: string
          q1: number
          q2: number
          q3: number
        }[]
      }
      highest_grossing_without_cinemascore: {
        Args: Record<PropertyKey, never>
        Returns: {
          box_office: number
          id: string
          release_date: string
          title: string
        }[]
      }
      ids_to_info: {
        Args: { ids: string[] }
        Returns: {
          budget: number
          poster_path: string
          release_date: string
          return_id: string
          title: string
          total_revenue: number
        }[]
      }
      knn: {
        Args: {
          k: number
          movie_id_og: string
          restrict_before?: boolean
          weights?: Json
        }
        Returns: {
          budget: number
          return_id: string
          similarity: number
          title: string
        }[]
      }
      knn_inside: {
        Args: {
          k: number
          movie_id_og: string
          restrict_before?: boolean
          weights?: Json
        }
        Returns: {
          budget: number
          return_id: string
          similarity: number
          title: string
        }[]
      }
      market_share: {
        Args: { category: string; end_date?: string; start_date?: string }
        Returns: {
          category_item: string
          market_share: number
          total_revenue: number
        }[]
      }
      movie_weekends: {
        Args: { input_id: string }
        Returns: {
          is_estimate: boolean
          is_new_release: boolean
          return_id: string
          weekend_num: number
          weekend_revenue: number
          weekend_start_date: string
          weekend_theaters: number
        }[]
      }
      mpaa_rating_counts: {
        Args: Record<PropertyKey, never>
        Returns: {
          count: number
          rating: string
        }[]
      }
      opening_day_data: {
        Args: Record<PropertyKey, never>
        Returns: {
          budget: number
          day_before_imdb_rating: number
          day_before_wikipedia_views: number
          day_before_youtube_sum_1_views: number
          day_before_youtube_sum_3_views: number
          day_before_youtube_sum_all_views: number
          genre: string
          in_franchise: boolean
          movie_id: string
          opening_date: string
          opening_day_revenue: number
          pre_release_cumulative_wikipedia_views: number
          production_method: string
          title: string
        }[]
      }
      percent_ranks: {
        Args: { input_id: string }
        Returns: {
          category: string
          percent_rank: number
          value: number
        }[]
      }
      preview_comparison: {
        Args: Record<PropertyKey, never>
        Returns: {
          first_3_days_revenue: number
          first_7_days_revenue: number
          first_day_revenue: number
          preview_revenue: number
          return_id: string
          title: string
          total_revenue: number
        }[]
      }
      production_company_counts: {
        Args: Record<PropertyKey, never>
        Returns: {
          company: string
          count: number
        }[]
      }
      production_country_counts: {
        Args: Record<PropertyKey, never>
        Returns: {
          count: number
          country: string
        }[]
      }
      production_method_counts: {
        Args: Record<PropertyKey, never>
        Returns: {
          count: number
          method: string
        }[]
      }
      refresh_screener_view: {
        Args: Record<PropertyKey, never>
        Returns: undefined
      }
      search_movies: {
        Args: { limit_count: number; search_term: string }
        Returns: {
          distance: number
          id: string
          release_date: string
          title: string
        }[]
      }
      source_counts: {
        Args: Record<PropertyKey, never>
        Returns: {
          count: number
          source: string
        }[]
      }
      spoken_language_counts: {
        Args: Record<PropertyKey, never>
        Returns: {
          count: number
          language: string
        }[]
      }
      sum_by_day: {
        Args: { end_date: string; filter_x_days: number; start_date: string }
        Returns: {
          budget_sum: number
          date: string
          revenue: number
          theater_count: number
          theater_weighted_budget: number
        }[]
      }
      topx: {
        Args: { x: number }
        Returns: {
          return_id: string
          title: string
          total_revenue: number
        }[]
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
