"""empty message

Revision ID: c5d666e27bef
Revises: da6768847878
Create Date: 2023-10-18 09:55:52.359496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5d666e27bef'
down_revision: Union[str, None] = 'da6768847878'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('balances', sa.Column('amount', sa.Float(), nullable=True))
    op.drop_column('balances', 'balance')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('balances', sa.Column('balance', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.drop_column('balances', 'amount')
    # ### end Alembic commands ###