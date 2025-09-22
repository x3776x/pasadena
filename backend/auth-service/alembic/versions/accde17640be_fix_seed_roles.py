"""fix_seed_roles

Revision ID: accde17640be
Revises: 0fd411f12522
Create Date: 2025-09-22 02:41:23.036796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'accde17640be'
down_revision: Union[str, Sequence[str], None] = '0fd411f12522'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        INSERT INTO roles (name)
        VALUES ('administrator'), ('user')
    """)

def downgrade():
    with op.get_context().autocommit_block():
        op.execute(
            "DELETE FROM roles WHERE name IN ('administrator', 'user')"
        )
