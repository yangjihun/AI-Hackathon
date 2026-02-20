"""add episode video_url

Revision ID: 0004_episode_video_url
Revises: 0003_subtitle_speaker_character
Create Date: 2026-02-19 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '0004_episode_video_url'
down_revision: str | None = '0003_subtitle_speaker_character'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('episodes', sa.Column('video_url', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('episodes', 'video_url')

