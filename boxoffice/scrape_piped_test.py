from scrape.movie_info import get_youtube_trailer_views

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: youtube_trailer_views.py <title> <year>")
        sys.exit(1)

    title = " ".join(sys.argv[1:-1])
    year = int(sys.argv[-1])

    result = get_youtube_trailer_views(title, year)

    if result is not None:
        print(result.youtube_sum_1_views)
        print(result.youtube_sum_3_views)
        print(result.youtube_sum_all_views)
    else:
        print("No results found")