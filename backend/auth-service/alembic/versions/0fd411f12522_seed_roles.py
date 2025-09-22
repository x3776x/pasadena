"""seed_roles

Revision ID: 0fd411f12522
Revises: 3b03ce98e5ac
Create Date: 2025-09-22 02:18:05.588473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0fd411f12522'
down_revision: Union[str, Sequence[str], None] = '3b03ce98e5ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        "INSERT INTO roles (name) VALUES "
        "('administrator'), "
        "('user')"           
    )


def downgrade():
    op.execute("DELETE FROM roles WHERE name IN ('administrator', 'user')")