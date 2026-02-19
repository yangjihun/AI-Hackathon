from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.errors import validation_error
from app.api.schemas import (
    Episode,
    EpisodeCreateRequest,
    IngestSubtitleLinesResponse,
    SubtitleLineBulkRequest,
    Title,
    TitleCreateRequest,
    AuthUser,
)
from app.db.models import Episode as EpisodeModel
from app.db.models import SubtitleLine, Title as TitleModel

router = APIRouter(prefix='/ingest', tags=['Ingestion'])


def _now() -> datetime:
    return datetime.now(timezone.utc)


@router.post('/titles', response_model=Title, status_code=status.HTTP_201_CREATED)
def ingest_title(
    payload: TitleCreateRequest,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(get_current_user),
) -> Title:
    row = TitleModel(name=payload.name.strip(), description=payload.description, created_at=_now())
    db.add(row)
    db.commit()
    db.refresh(row)
    return Title(
        id=row.id,
        name=row.name,
        description=row.description,
        created_at=row.created_at.isoformat() if row.created_at else None,
    )


@router.post('/episodes', response_model=Episode, status_code=status.HTTP_201_CREATED)
def ingest_episode(
    payload: EpisodeCreateRequest,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(get_current_user),
) -> Episode:
    title = db.scalar(select(TitleModel).where(TitleModel.id == payload.title_id))
    if title is None:
        raise validation_error('Invalid request.', {'field': 'title_id', 'reason': 'Title not found'})

    row = EpisodeModel(
        title_id=payload.title_id,
        season=payload.season,
        episode_number=payload.episode_number,
        name=payload.name,
        duration_ms=payload.duration_ms,
        created_at=_now(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return Episode(
        id=row.id,
        title_id=row.title_id,
        season=row.season,
        episode_number=row.episode_number,
        name=row.name,
        duration_ms=row.duration_ms,
    )


@router.post('/subtitle-lines:bulk', response_model=IngestSubtitleLinesResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest_subtitle_lines_bulk(
    payload: SubtitleLineBulkRequest,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(get_current_user),
) -> IngestSubtitleLinesResponse:
    episode_ids = sorted({line.episode_id for line in payload.lines})
    existing_episodes = set(
        db.scalars(select(EpisodeModel.id).where(EpisodeModel.id.in_(episode_ids))).all()
    )
    missing = [episode_id for episode_id in episode_ids if episode_id not in existing_episodes]
    if missing:
        raise validation_error(
            'Invalid request.',
            {'field': 'episode_id', 'reason': f'Episode not found: {missing[0]}'},
        )

    inserted = 0
    for line in payload.lines:
        row = SubtitleLine(
            episode_id=line.episode_id,
            start_ms=line.start_ms,
            end_ms=line.end_ms,
            speaker_text=line.speaker_text,
            speaker_character_id=line.speaker_character_id,
            text=line.text,
            created_at=_now(),
        )
        db.add(row)
        inserted += 1

    db.commit()
    return IngestSubtitleLinesResponse(
        inserted_count=inserted,
        queued_embedding_jobs=inserted,
    )

