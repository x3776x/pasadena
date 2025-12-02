from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "first_version"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Tabla artist
    op.create_table(
        "artist",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
    )

    # 2. Tabla genre
    op.create_table(
        "genre",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
    )

    # 3. Tabla album
    op.create_table(
        "album",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("release_date", sa.Date),
        sa.Column("cover", sa.LargeBinary),
        sa.Column(
            "artist_id",
            sa.Integer,
            sa.ForeignKey("artist.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # 4. Tabla song
    op.create_table(
        "song",
        sa.Column("song_id", sa.String(100), primary_key=True),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("duration", sa.Float),
        sa.Column(
            "album_id",
            sa.Integer,
            sa.ForeignKey("album.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "genre_id",
            sa.Integer,
            sa.ForeignKey("genre.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "artist_id",
            sa.Integer,
            sa.ForeignKey("artist.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_table("song")
    op.drop_table("album")
    op.drop_table("genre")
    op.drop_table("artist")
