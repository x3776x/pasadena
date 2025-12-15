from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_user_statistics"
down_revision = "first_version"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_statistics",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.String(100), nullable=False),
        sa.Column("song_id", sa.String(100), sa.ForeignKey("song.song_id", ondelete="CASCADE")),
        sa.Column("play_count", sa.Integer, nullable=False, default=0),
        sa.Column("total_time", sa.Float, nullable=False, default=0.0),
        sa.Column("last_play", sa.DateTime),
    )

    op.create_index("idx_user_statistics_user", "user_statistics", ["user_id"])
    op.create_index("idx_user_statistics_song", "user_statistics", ["song_id"])


def downgrade():
    op.drop_index("idx_user_statistics_user")
    op.drop_index("idx_user_statistics_song")
    op.drop_table("user_statistics")
