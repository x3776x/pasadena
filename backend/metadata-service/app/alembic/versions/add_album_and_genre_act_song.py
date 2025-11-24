"""add album and genre tables with relations to song"""


# Revisión
"""add album and genre tables with relations to song"""

from alembic import op
import sqlalchemy as sa


# Revisión
revision = "20251109_add_album_genre"
down_revision = None  # ✅ Es la primera migración del proyecto
branch_labels = None
depends_on = None



def upgrade():
    # Crear tabla genre
    op.create_table(
        "genre",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
    )

    # Crear tabla album
    op.create_table(
        "album",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("release_date", sa.Date),
        sa.Column("cover", sa.LargeBinary),  # <- aquí guardamos bytes[],
        sa.Column("artist")
    )

    # Agregar columnas a song
    op.add_column("song", sa.Column("album_id", sa.Integer, sa.ForeignKey("album.id", ondelete="SET NULL")))
    op.add_column("song", sa.Column("genre_id", sa.Integer, sa.ForeignKey("genre.id", ondelete="SET NULL")))


def downgrade():
    # Eliminar columnas y tablas si se hace rollback
    op.drop_column("song", "genre_id")
    op.drop_column("song", "album_id")
    op.drop_table("album")
    op.drop_table("genre")
