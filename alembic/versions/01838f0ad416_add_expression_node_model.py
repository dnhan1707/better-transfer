"""Add expression node model

Revision ID: 01838f0ad416
Revises: 2b554588fe62
Create Date: 2025-05-20 00:10:38.121031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01838f0ad416'
down_revision: Union[str, None] = '2b554588fe62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Create both tables WITHOUT the circular foreign keys
    op.create_table('expression_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('parent_node_id', sa.Integer(), nullable=True),
        sa.Column('node_type', sa.Enum('OPERATOR', 'COURSE', name='nodetype'), nullable=False),
        sa.Column('operator_type', sa.Enum('AND', 'OR', name='operatortype'), nullable=True),
        sa.Column('university_course_id', sa.Integer(), nullable=True),
        sa.ForeignKey('university_courses.id'),
        sa.ForeignKey('expression_nodes.id'),  # Self-reference is fine
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_expression_nodes_id', 'id')
    )
    
    op.create_table('articulation_group',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('university_id', sa.Integer(), nullable=False),
        sa.Column('major_id', sa.Integer(), nullable=False),
        sa.Column('college_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('root_expression_node_id', sa.Integer(), nullable=True),
        sa.ForeignKey('universities.id'),
        sa.ForeignKey('majors.id'),
        sa.ForeignKey('colleges.id'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_articulation_group_id', 'id')
    )
    
    # Step 2: Add the circular foreign keys after both tables exist
    op.create_foreign_key(
        'fk_articulation_group_root_expression_node', 
        'articulation_group', 'expression_nodes',
        ['root_expression_node_id'], ['id']
    )
    
    op.create_foreign_key(
        'fk_expression_nodes_group', 
        'expression_nodes', 'articulation_group',
        ['group_id'], ['id']
    )

def downgrade() -> None:
    # First drop the foreign key constraints
    op.drop_constraint('fk_expression_nodes_group', 'expression_nodes', type_='foreignkey')
    op.drop_constraint('fk_articulation_group_root_expression_node', 'articulation_group', type_='foreignkey')
    
    # Then drop the tables
    op.drop_index('ix_articulation_group_id', table_name='articulation_group')
    op.drop_table('articulation_group')
    op.drop_index('ix_expression_nodes_id', table_name='expression_nodes')
    op.drop_table('expression_nodes')
