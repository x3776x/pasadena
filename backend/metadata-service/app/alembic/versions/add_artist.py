"""add artist table and relations to song and album"""

from alembic import op
import sqlalchemy as sa


# Identificadores de migración
revision = "add_artist_table"
down_revision = "20251109_add_album_genre"  # ✅ Referencia a la migración anterior
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla artist
    op.create_table(
        "artist",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("country", sa.String(50)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Agregar columna artist_id a album
    op.add_column(
        "album",
        sa.Column(
            "artist_id",
            sa.Integer,
            sa.ForeignKey("artist.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # Agregar columna artist_id a song
    op.add_column(
        "song",
        sa.Column(
            "artist_id",
            sa.Integer,
            sa.ForeignKey("artist.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade():
    # Eliminar columnas y tabla si se hace rollback
    op.drop_column("song", "artist_id")
    op.drop_column("album", "artist_id")
    op.drop_table("artist")
