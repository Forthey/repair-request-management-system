"""empty message

Revision ID: 59fe036899d4
Revises: 
Create Date: 2024-05-07 19:28:49.676942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59fe036899d4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('activities',
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('applications_reasons',
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('close_reasons',
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('company_positions',
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('machines',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('photo_url', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('workers',
    sa.Column('telegram_id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('surname', sa.String(), nullable=False),
    sa.Column('patronymic', sa.String(), nullable=True),
    sa.Column('access_right', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('telegram_id')
    )
    op.create_table('clients',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('main_client_name', sa.String(), nullable=True),
    sa.Column('activity', sa.String(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['activity'], ['activities.name'], ),
    sa.ForeignKeyConstraint(['main_client_name'], ['clients.name'], ),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('addresses',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('photo_url', sa.String(), nullable=True),
    sa.Column('workhours', sa.String(), nullable=True),
    sa.Column('client_name', sa.String(), nullable=False),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['client_name'], ['clients.name'], ),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('contacts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('surname', sa.String(), nullable=False),
    sa.Column('patronymic', sa.String(), nullable=True),
    sa.Column('client_name', sa.String(), nullable=False),
    sa.Column('company_position', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone1', sa.String(), nullable=True),
    sa.Column('phone2', sa.String(), nullable=True),
    sa.Column('phone3', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['client_name'], ['clients.name'], ),
    sa.ForeignKeyConstraint(['company_position'], ['company_positions.name'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('applications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('main_application_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('est_repair_date', sa.DateTime(), nullable=True),
    sa.Column('est_repair_duration_hours', sa.Integer(), nullable=True),
    sa.Column('editor_id', sa.BigInteger(), nullable=False),
    sa.Column('repairer_id', sa.BigInteger(), nullable=True),
    sa.Column('client_name', sa.String(), nullable=True),
    sa.Column('contact_id', sa.Integer(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('machine', sa.String(), nullable=True),
    sa.Column('closed_at', sa.DateTime(), nullable=True),
    sa.Column('close_reason', sa.String(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['address'], ['addresses.name'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['client_name'], ['clients.name'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['close_reason'], ['close_reasons.name'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['editor_id'], ['workers.telegram_id'], ),
    sa.ForeignKeyConstraint(['machine'], ['machines.name'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['main_application_id'], ['applications.id'], ),
    sa.ForeignKeyConstraint(['repairer_id'], ['workers.telegram_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rel_reasons_applications',
    sa.Column('reason_name', sa.String(), nullable=False),
    sa.Column('application_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['reason_name'], ['applications_reasons.name'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('reason_name', 'application_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rel_reasons_applications')
    op.drop_table('applications')
    op.drop_table('contacts')
    op.drop_table('addresses')
    op.drop_table('clients')
    op.drop_table('workers')
    op.drop_table('machines')
    op.drop_table('company_positions')
    op.drop_table('close_reasons')
    op.drop_table('applications_reasons')
    op.drop_table('activities')
    # ### end Alembic commands ###
