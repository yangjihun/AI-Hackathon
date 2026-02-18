from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select

from app.db.base import Base
from app.db.models import Episode, Title
from app.db.session import SessionLocal, engine


def now() -> datetime:
    return datetime.now(timezone.utc)


CATALOG_FIXTURES: list[dict] = [
    {
        "name": "Demo Thriller A",
        "description": "A detective thriller with trust and betrayal.",
        "episode_name": "S1E1 - Suspicion Begins",
    },
    {
        "name": "Mystery Casebook",
        "description": "Cold clues and layered alibis in a city mystery.",
        "episode_name": "S1E1 - First Clue",
    },
    {
        "name": "Shadow Portrait",
        "description": "A drama where relationships shift each episode.",
        "episode_name": "S1E1 - The Hidden Face",
    },
    {
        "name": "Trail of Evidence",
        "description": "Investigators race against a changing narrative.",
        "episode_name": "S1E1 - Start of the Chase",
    },
    {
        "name": "Lost Memory",
        "description": "Fragments of memory reveal a deeper truth.",
        "episode_name": "S1E1 - Broken Pieces",
    },
    {
        "name": "Secret Chamber",
        "description": "A family secret unfolds into a tense thriller.",
        "episode_name": "S1E1 - Door Locked",
    },
]


def seed_catalog() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    created_titles = 0
    created_episodes = 0

    try:
        for item in CATALOG_FIXTURES:
            title = db.scalar(select(Title).where(Title.name == item["name"]))
            if title is None:
                title = Title(
                    name=item["name"],
                    description=item["description"],
                    created_at=now(),
                )
                db.add(title)
                db.flush()
                created_titles += 1
            else:
                if not title.description:
                    title.description = item["description"]

            episode = db.scalar(
                select(Episode).where(
                    Episode.title_id == title.id,
                    Episode.season == 1,
                    Episode.episode_number == 1,
                )
            )
            if episode is None:
                episode = Episode(
                    title_id=title.id,
                    season=1,
                    episode_number=1,
                    name=item["episode_name"],
                    duration_ms=3_600_000,
                    created_at=now(),
                )
                db.add(episode)
                created_episodes += 1

        db.commit()
        total_titles = db.scalar(select(func.count()).select_from(Title))
        print(f"Catalog seed complete: +{created_titles} titles, +{created_episodes} episodes")
        print(f"Total titles: {total_titles}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_catalog()
