"""add subtitle speaker_character_id

Revision ID: 0003_subtitle_speaker_character
Revises: 0002_users_auth
Create Date: 2026-02-18 18:20:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '0003_subtitle_speaker_character'
down_revision: str | None = '0002_users_auth'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('subtitle_lines', sa.Column('speaker_character_id', sa.String(length=36), nullable=True))
    op.create_foreign_key(
        'fk_subtitle_lines_speaker_character_id',
        'subtitle_lines',
        'characters',
        ['speaker_character_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_subtitle_lines_speaker_character_id', 'subtitle_lines', type_='foreignkey')
    op.drop_column('subtitle_lines', 'speaker_character_id')

