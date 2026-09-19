from scrape.cache_people import people_cache
from scrape.scrape_types import CastOrCrewInsert, Credit, PersonToInsert


def add_castorcrews_to_database(
    castorcrews: list[Credit],
    movie_id: str,
) -> None:
    # first want to bulk create the person rows and then bulk create the cast or crew rows
    people_to_create: dict[int, PersonToInsert] = {
        castorcrew.person_tmdb_id: PersonToInsert(
            name=castorcrew.person_name,
            tmdb_id=castorcrew.person_tmdb_id,
            profile_path=castorcrew.person_profile_path,
        )
        for castorcrew in castorcrews
    }

    id_map = people_cache.bulk_create_people(people_to_create)

    cast_or_crews_to_create: list[CastOrCrewInsert] = []

    for castorcrew in castorcrews:
        person_id = id_map[castorcrew.person_tmdb_id]

        cast_or_crews_to_create.append(
            CastOrCrewInsert(
                movie_id=movie_id,
                person_id=person_id,
                is_cast=castorcrew.is_cast,
                character_name=castorcrew.character_name,
                credit_order=castorcrew.credit_order,
                department=castorcrew.department,
                job=castorcrew.job,
            )
        )

    people_cache.bulk_create_cast_or_crew(cast_or_crews_to_create)
