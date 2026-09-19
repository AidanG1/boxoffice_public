from scrape.wikipedia_search import get_wikipedia_information


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: wikipedia_search.py <title> <year>")
        sys.exit(1)

    title = " ".join(sys.argv[1:-1])
    year = int(sys.argv[-1])

    result = get_wikipedia_information(title, year)

    if result is not None:
        print(result.title)
        print(result.excerpt)
        if result.description is not None:
            print(result.description)
        if result.thumbnail is not None:
            print(result.thumbnail.url)

    else:
        print("No results found")