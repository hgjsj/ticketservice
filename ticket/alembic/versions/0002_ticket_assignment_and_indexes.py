"""add ticket assignment fields and indexes

Revision ID: 0002_ticket_assignment_and_indexes
Revises: 0001_init
Create Date: 2026-08-12
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_ticket_assignment_and_indexes"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tickets: assignee/audit fields + query indexes.
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.add_column(sa.Column("assignee_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("closed_at", sa.DateTime(), nullable=True))
        batch_op.create_index("ix_tickets_creator_id", ["creator_id"], unique=False)
        batch_op.create_index("ix_tickets_assignee_id", ["assignee_id"], unique=False)
        batch_op.create_index("ix_tickets_status", ["status"], unique=False)
        batch_op.create_index("ix_tickets_priority", ["priority"], unique=False)
        batch_op.create_foreign_key(
            "fk_tickets_assignee_id_users",
            "users",
            ["assignee_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.execute("UPDATE tickets SET updated_at = created_at WHERE updated_at IS NULL")

    with op.batch_alter_table("tickets") as batch_op:
        batch_op.alter_column("updated_at", existing_type=sa.DateTime(), nullable=False)

    # Comments: index ticket_id for timeline queries.
    with op.batch_alter_table("comments") as batch_op:
        batch_op.create_index("ix_comments_ticket_id", ["ticket_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("comments") as batch_op:
        batch_op.drop_index("ix_comments_ticket_id")

    with op.batch_alter_table("tickets") as batch_op:
        batch_op.drop_constraint("fk_tickets_assignee_id_users", type_="foreignkey")
        batch_op.drop_index("ix_tickets_priority")
        batch_op.drop_index("ix_tickets_status")
        batch_op.drop_index("ix_tickets_assignee_id")
        batch_op.drop_index("ix_tickets_creator_id")
        batch_op.drop_column("closed_at")
        batch_op.drop_column("updated_at")
        batch_op.drop_column("assignee_id")
