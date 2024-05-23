"""create_main_users

Revision ID: ab82b282b78c
Revises: f175400992d8
Create Date: 2024-05-23 11:24:51.239294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from database.models.worker_orm import WorkerORM

# revision identifiers, used by Alembic.
revision: str = 'ab82b282b78c'
down_revision: Union[str, None] = '629229bef5c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    admin1 = WorkerORM(
        telegram_id="1319924607",
        name="Никита",
        surname="Дрекалов",
        access_right="Админ"
    )
    admin2 = WorkerORM(
        telegram_id="1663663528",
        name="Никита",
        surname="Адейкин",
        access_right="Админ"
    )

    op.execute(
        insert(WorkerORM)
        .values([
            {
                "telegram_id": "1663663528",
                "name": "Никита",
                "surname": "Адейкин",
                "access_right": "Админ"
            },
            {
                "telegram_id": "1319924607",
                "name": "Никита",
                "surname": "Дрекалов",
                "access_right": "Админ"

            }
        ])
        .on_conflict_do_nothing(
            index_elements=['telegram_id']
        )
    )


def downgrade() -> None:
    pass
