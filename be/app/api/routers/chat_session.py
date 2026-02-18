from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.errors import not_found, validation_error
from app.api.schemas import (
    ChatMessageCreateRequest,
    ChatMessageListResponse,
    ChatMessageOut,
    ChatSessionCreateRequest,
    ChatSessionListResponse,
    ChatSessionOut,
)
from app.db.models import ChatMessage, ChatSession, Episode, Title, User

router = APIRouter(prefix='/chat', tags=['ChatSession'])


def _serialize_session(session: ChatSession) -> ChatSessionOut:
    return ChatSessionOut(
        id=session.id,
        title_id=session.title_id,
        episode_id=session.episode_id,
        user_id=session.user_id or '',
        current_time_ms=session.current_time_ms,
        meta=session.meta or {},
        created_at=session.created_at.isoformat() if session.created_at else None,
    )


def _serialize_message(message: ChatMessage) -> ChatMessageOut:
    return ChatMessageOut(
        id=message.id,
        session_id=message.session_id,
        role=message.role,
        content=message.content,
        current_time_ms=message.current_time_ms,
        model=message.model,
        prompt_tokens=message.prompt_tokens,
        completion_tokens=message.completion_tokens,
        related_relation_id=message.related_relation_id,
        created_at=message.created_at.isoformat() if message.created_at else None,
    )


@router.post('/sessions', response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
def create_chat_session(payload: ChatSessionCreateRequest, db: Session = Depends(get_db)) -> ChatSessionOut:
    title = db.scalar(select(Title).where(Title.id == payload.title_id))
    if title is None:
        raise validation_error('Invalid request.', {'field': 'title_id', 'reason': 'Title not found'})

    episode = db.scalar(select(Episode).where(Episode.id == payload.episode_id))
    if episode is None:
        raise validation_error('Invalid request.', {'field': 'episode_id', 'reason': 'Episode not found'})

    user = db.scalar(select(User).where(User.id == payload.user_id))
    if user is None:
        raise validation_error('Invalid request.', {'field': 'user_id', 'reason': 'User not found'})

    session = ChatSession(
        title_id=payload.title_id,
        episode_id=payload.episode_id,
        user_id=payload.user_id,
        current_time_ms=payload.current_time_ms,
        meta=payload.meta,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return _serialize_session(session)


@router.get('/sessions', response_model=ChatSessionListResponse)
def list_chat_sessions(
    title_id: str | None = None,
    episode_id: str | None = None,
    user_id: str | None = None,
    db: Session = Depends(get_db),
) -> ChatSessionListResponse:
    stmt = select(ChatSession)
    if title_id:
        stmt = stmt.where(ChatSession.title_id == title_id)
    if episode_id:
        stmt = stmt.where(ChatSession.episode_id == episode_id)
    if user_id:
        stmt = stmt.where(ChatSession.user_id == user_id)
    stmt = stmt.order_by(ChatSession.created_at.desc())

    sessions = list(db.scalars(stmt).all())
    return ChatSessionListResponse(items=[_serialize_session(item) for item in sessions])


@router.get('/sessions/{sessionId}', response_model=ChatSessionOut)
def get_chat_session(sessionId: str, db: Session = Depends(get_db)) -> ChatSessionOut:
    session = db.scalar(select(ChatSession).where(ChatSession.id == sessionId))
    if session is None:
        raise not_found()
    return _serialize_session(session)


@router.get('/sessions/{sessionId}/messages', response_model=ChatMessageListResponse)
def list_chat_messages(
    sessionId: str,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> ChatMessageListResponse:
    session = db.scalar(select(ChatSession).where(ChatSession.id == sessionId))
    if session is None:
        raise not_found()

    messages = list(
        db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == sessionId)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        ).all()
    )

    return ChatMessageListResponse(session_id=sessionId, items=[_serialize_message(item) for item in messages])


@router.post('/sessions/{sessionId}/messages', response_model=ChatMessageOut, status_code=status.HTTP_201_CREATED)
def create_chat_message(
    sessionId: str,
    payload: ChatMessageCreateRequest,
    db: Session = Depends(get_db),
) -> ChatMessageOut:
    session = db.scalar(select(ChatSession).where(ChatSession.id == sessionId))
    if session is None:
        raise not_found()

    message = ChatMessage(
        session_id=sessionId,
        role=payload.role.value,
        content=payload.content,
        current_time_ms=payload.current_time_ms,
        model=payload.model,
        prompt_tokens=payload.prompt_tokens,
        completion_tokens=payload.completion_tokens,
        related_relation_id=payload.related_relation_id,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return _serialize_message(message)

