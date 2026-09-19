from scrape.scrape_types import Credit, Credits


def convert_credits_to_cast_or_crew(credits: Credits) -> list[Credit]:
    new_credits: list[Credit] = []

    for cast in credits.cast:
        new_credits.append(
            Credit(
                is_cast=True,
                character_name=cast.character,
                credit_order=cast.order,
                department=None,
                job=None,
                person_tmdb_id=cast.id,
                person_name=cast.name,
                person_profile_path=cast.profile_path,
            )
        )

    for crew in credits.crew:
        # filter for only the most important
        if crew.job not in [
            "Director",
            "Producer",
            "Screenplay",
            "Story",
            "Original Music Composer",
            "Director of Photography",
            "Editor",
            "Book",
            "Novel",
            "Characters",
            "Writer",
            "Editor",
        ]:
            continue

        new_credits.append(
            Credit(
                is_cast=False,
                character_name=None,
                credit_order=None,
                department=crew.department,
                job=crew.job,
                person_tmdb_id=crew.id,
                person_name=crew.name,
                person_profile_path=crew.profile_path,
            )
        )

    return new_credits
