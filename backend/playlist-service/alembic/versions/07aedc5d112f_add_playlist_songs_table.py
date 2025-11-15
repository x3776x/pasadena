"""add playlist_songs table

Revision ID: 07aedc5d112f
Revises: b7c2e1f3a4d6
Create Date: 2025-11-07 22:38:53.429437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07aedc5d112f'
down_revision: Union[str, Sequence[str], None] = 'b7c2e1f3a4d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'playlist_songs',
        sa.Column('playlist_id', sa.Integer, sa.ForeignKey('playlist.id', ondelete='CASCADE'), nullable=False),
        sa.Column('song_id', sa.String(length=100), nullable=False),
        sa.Column('position', sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint('playlist_id', 'song_id')
    )
    op.create_index(op.f('ix_playlist_songs_playlist_id'), 'playlist_songs', ['playlist_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_playlist_songs_playlist_id'), table_name='playlist_songs')
    op.drop_table('playlist_songs')
