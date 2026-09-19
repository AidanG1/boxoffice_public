# Utility function to get the database id for a movie based on its slug from numbers

from scrape.scrape_types import (
    CastOrCrewInsert,
    PersonToInsert,
)
from database.db import supabase
from supabase import PostgrestAPIResponse
from database.types import (
    Person,
)
from typing import Optional
from colors import bcolors


class PeopleCache:
    people_cache: dict[int, str] = {}

    def get_person_id(self, tmdb_id: int) -> str | None:
        # send a request to the database to get the person id
        # if it doesn't exist, return None
        person: PostgrestAPIResponse[Person] = (
            supabase.table("person").select("id").eq("tmdb_id", tmdb_id).execute()
        )

        if not person.data:
            return None

        return person.data[0]["id"]

    def get_or_create_person(
        self, name: str, tmdb_id: int, profile_path: Optional[str]
    ) -> str:
        person_id = self.get_person_id(tmdb_id)

        if person_id is None:
            person: PostgrestAPIResponse[Person] = (
                supabase.table("person")
                .insert(
                    {"name": name, "tmdb_id": tmdb_id, "profile_path": profile_path}
                )
                .execute()
            )

            first = person.data[0]

            # add the person to the cache
            self.people_cache[tmdb_id] = first["id"]

            print(
                f"{bcolors.OKGREEN}Added person {name} with tmdb id {tmdb_id}{bcolors.ENDC}. Cache value: {self.people_cache[tmdb_id]}"
            )

            return first["id"]

        return person_id

    def create_castorcrew(
        self,
        movie_id: str,
        person_id: str,
        is_cast: bool,
        character_name: Optional[str],
        credit_order: Optional[int],
        department: Optional[str],
        job: Optional[str],
    ) -> None:
        supabase.table("castorcrew").insert(
            {
                "movie_id": movie_id,
                "person_id": person_id,
                "is_cast": is_cast,
                "character_name": character_name,
                "credit_order": credit_order,
                "department": department,
                "job": job,
            }
        ).execute()

    def bulk_create_people(
        self, people_to_create: dict[int, PersonToInsert]
    ) -> dict[int, str]:
        people_to_return: dict[int, str] = {}

        if len(people_to_create) == 0:
            return people_to_return

        # need to check if the people already exist
        ids_to_check: list[int] = list(people_to_create.keys())

        existing_people: PostgrestAPIResponse[Person] = (
            supabase.table("person")
            .select("id", "tmdb_id")
            .in_("tmdb_id", ids_to_check)
            .execute()
        )

        for person in existing_people.data:
            people_to_return[person["tmdb_id"]] = person["id"]
            people_to_create.pop(person["tmdb_id"])

        if len(people_to_create) == 0:
            print(f"{bcolors.OKCYAN}No new people to create{bcolors.ENDC}")
            return people_to_return

        dump = [person.model_dump() for person in people_to_create.values()]

        try:
            people: PostgrestAPIResponse[Person] = (
                supabase.table("person").insert(dump).execute()
            )
            for person in people.data:
                people_to_return[person["tmdb_id"]] = person["id"]

            print(
                f"{bcolors.OKGREEN}Bulk created {len(people_to_create)} people{bcolors.ENDC}"
            )

            return people_to_return
        except Exception as e:
            print(f"{bcolors.FAIL}Error: {e}{bcolors.ENDC}")
            print(f"{bcolors.FAIL}Dump: {dump}{bcolors.ENDC}")
            raise e

    def bulk_create_cast_or_crew(
        self, cast_or_crew_to_create: list[CastOrCrewInsert]
    ) -> None:
        if len(cast_or_crew_to_create) == 0:
            print(f"{bcolors.OKCYAN}No new cast or crew to create{bcolors.ENDC}")
            return

        response: PostgrestAPIResponse[CastOrCrewInsert] = (
            supabase.table("castorcrew")
            .insert(
                [cast_or_crew.model_dump() for cast_or_crew in cast_or_crew_to_create]
            )
            .execute()
        )

        print(
            f"{bcolors.OKGREEN}Bulk created {len(response.data)} cast or crew{bcolors.ENDC}"
        )


people_cache = PeopleCache()
