"""Init migration

Revision ID: 74f122ee6ba7
Revises: 
Create Date: 2024-04-01 21:07:09.170194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74f122ee6ba7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('access_rights',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('notes', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('applications_reasons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('reason', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company_positions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('position', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('machines',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('photo_url', sa.String(), nullable=True),
    sa.Column('release_year', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('clients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('main_client_id', sa.Integer(), nullable=True),
    sa.Column('activity_id', sa.Integer(), nullable=False),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
    sa.ForeignKeyConstraint(['main_client_id'], ['clients.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('contacts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('surname', sa.String(), nullable=False),
    sa.Column('patronymic', sa.String(), nullable=True),
    sa.Column('company_position_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone1', sa.String(), nullable=True),
    sa.Column('phone2', sa.String(), nullable=True),
    sa.Column('phone3', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['company_position_id'], ['company_positions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('workers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('telegram_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('surname', sa.String(), nullable=False),
    sa.Column('patronymic', sa.String(), nullable=True),
    sa.Column('access_rights_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['access_rights_id'], ['access_rights.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('telegram_id')
    )
    op.create_table('addresses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('photo_url', sa.String(), nullable=True),
    sa.Column('workhours', sa.String(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('address')
    )
    op.create_table('applications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('main_application_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('est_repair_date', sa.DateTime(), nullable=True),
    sa.Column('est_repair_duration_hours', sa.Integer(), nullable=True),
    sa.Column('editor_id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('repairer_id', sa.Integer(), nullable=True),
    sa.Column('contact_id', sa.Integer(), nullable=True),
    sa.Column('address_id', sa.Integer(), nullable=False),
    sa.Column('machine_id', sa.Integer(), nullable=False),
    sa.Column('closed_at', sa.DateTime(), nullable=True),
    sa.Column('close_reason', sa.DateTime(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ),
    sa.ForeignKeyConstraint(['editor_id'], ['workers.id'], ),
    sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ),
    sa.ForeignKeyConstraint(['main_application_id'], ['applications.id'], ),
    sa.ForeignKeyConstraint(['repairer_id'], ['workers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rel_reasons_applications',
    sa.Column('reason_id', sa.Integer(), nullable=False),
    sa.Column('application_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
    sa.ForeignKeyConstraint(['reason_id'], ['applications_reasons.id'], ),
    sa.PrimaryKeyConstraint('reason_id', 'application_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rel_reasons_applications')
    op.drop_table('applications')
    op.drop_table('addresses')
    op.drop_table('workers')
    op.drop_table('contacts')
    op.drop_table('clients')
    op.drop_table('machines')
    op.drop_table('company_positions')
    op.drop_table('applications_reasons')
    op.drop_table('activities')
    op.drop_table('access_rights')
    # ### end Alembic commands ###
