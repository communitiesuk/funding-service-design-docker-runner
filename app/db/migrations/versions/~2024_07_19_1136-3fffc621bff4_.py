"""empty message

Revision ID: 3fffc621bff4
Revises: 5c63de4e4e49
Create Date: 2024-07-19 11:36:32.716999

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3fffc621bff4"
down_revision = "5c63de4e4e49"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("page", schema=None) as batch_op:
        batch_op.add_column(sa.Column("controller", sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("page", schema=None) as batch_op:
        batch_op.drop_column("controller")

    # ### end Alembic commands ###