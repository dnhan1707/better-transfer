"""Update articulation_group structure

Revision ID: 8b596fbbbe28
Revises: 74c0ef1184a1
Create Date: 2025-05-16 20:40:20.505325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8b596fbbbe28'
down_revision: Union[str, None] = '74c0ef1184a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('articulation_group', sa.Column('college_id', sa.Integer(), nullable=False))
    op.add_column('articulation_group', sa.Column('expression', sa.JSON(), nullable=False))
    op.create_foreign_key(None, 'articulation_group', 'colleges', ['college_id'], ['id'])
    op.drop_column('articulation_group', 'university_course_ids')
    op.drop_column('articulation_group', 'operator')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('articulation_group', sa.Column('operator', postgresql.ENUM('AND', 'OR', name='relationshiptype'), autoincrement=False, nullable=False))
    op.add_column('articulation_group', sa.Column('university_course_ids', postgresql.ARRAY(sa.INTEGER()), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'articulation_group', type_='foreignkey')
    op.drop_column('articulation_group', 'expression')
    op.drop_column('articulation_group', 'college_id')
    # ### end Alembic commands ###
