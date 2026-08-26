"""enforce ondelete rules on sqlite foreign keys

Revision ID: 0003_enforce_ondelete_rules
Revises: 0002_ticket_assignment_and_indexes
Create Date: 2026-08-12
"""

from alembic import op


revision = "0003_enforce_ondelete_rules"
down_revision = "0002_ticket_assignment_and_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("PRAGMA foreign_keys=OFF")

    op.execute(
        """
        CREATE TABLE tickets_new (
            id INTEGER NOT NULL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            status VARCHAR(11) NOT NULL,
            priority VARCHAR(6) NOT NULL,
            creator_id INTEGER NOT NULL,
            created_at DATETIME NOT NULL,
            assignee_id INTEGER,
            updated_at DATETIME NOT NULL,
            closed_at DATETIME,
            FOREIGN KEY(creator_id) REFERENCES users(id) ON DELETE RESTRICT,
            FOREIGN KEY(assignee_id) REFERENCES users(id) ON DELETE SET NULL
        )
        """
    )
    op.execute(
        """
        INSERT INTO tickets_new (
            id, title, description, status, priority, creator_id,
            created_at, assignee_id, updated_at, closed_at
        )
        SELECT
            id, title, description, status, priority, creator_id,
            created_at, assignee_id, updated_at, closed_at
        FROM tickets
        """
    )
    op.execute("DROP TABLE tickets")
    op.execute("ALTER TABLE tickets_new RENAME TO tickets")

    op.execute("CREATE INDEX ix_tickets_id ON tickets (id)")
    op.execute("CREATE INDEX ix_tickets_title ON tickets (title)")
    op.execute("CREATE INDEX ix_tickets_creator_id ON tickets (creator_id)")
    op.execute("CREATE INDEX ix_tickets_assignee_id ON tickets (assignee_id)")
    op.execute("CREATE INDEX ix_tickets_status ON tickets (status)")
    op.execute("CREATE INDEX ix_tickets_priority ON tickets (priority)")

    op.execute(
        """
        CREATE TABLE comments_new (
            id INTEGER NOT NULL PRIMARY KEY,
            content TEXT NOT NULL,
            ticket_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
            FOREIGN KEY(author_id) REFERENCES users(id) ON DELETE RESTRICT
        )
        """
    )
    op.execute(
        """
        INSERT INTO comments_new (id, content, ticket_id, author_id, created_at)
        SELECT id, content, ticket_id, author_id, created_at FROM comments
        """
    )
    op.execute("DROP TABLE comments")
    op.execute("ALTER TABLE comments_new RENAME TO comments")

    op.execute("CREATE INDEX ix_comments_id ON comments (id)")
    op.execute("CREATE INDEX ix_comments_ticket_id ON comments (ticket_id)")

    op.execute("PRAGMA foreign_keys=ON")


def downgrade() -> None:
    op.execute("PRAGMA foreign_keys=OFF")

    op.execute(
        """
        CREATE TABLE comments_old (
            id INTEGER NOT NULL PRIMARY KEY,
            content TEXT NOT NULL,
            ticket_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY(ticket_id) REFERENCES tickets(id),
            FOREIGN KEY(author_id) REFERENCES users(id)
        )
        """
    )
    op.execute(
        """
        INSERT INTO comments_old (id, content, ticket_id, author_id, created_at)
        SELECT id, content, ticket_id, author_id, created_at FROM comments
        """
    )
    op.execute("DROP TABLE comments")
    op.execute("ALTER TABLE comments_old RENAME TO comments")

    op.execute("CREATE INDEX ix_comments_id ON comments (id)")
    op.execute("CREATE INDEX ix_comments_ticket_id ON comments (ticket_id)")

    op.execute(
        """
        CREATE TABLE tickets_old (
            id INTEGER NOT NULL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            status VARCHAR(11) NOT NULL,
            priority VARCHAR(6) NOT NULL,
            creator_id INTEGER NOT NULL,
            created_at DATETIME NOT NULL,
            assignee_id INTEGER,
            updated_at DATETIME NOT NULL,
            closed_at DATETIME,
            FOREIGN KEY(creator_id) REFERENCES users(id),
            FOREIGN KEY(assignee_id) REFERENCES users(id) ON DELETE SET NULL
        )
        """
    )
    op.execute(
        """
        INSERT INTO tickets_old (
            id, title, description, status, priority, creator_id,
            created_at, assignee_id, updated_at, closed_at
        )
        SELECT
            id, title, description, status, priority, creator_id,
            created_at, assignee_id, updated_at, closed_at
        FROM tickets
        """
    )
    op.execute("DROP TABLE tickets")
    op.execute("ALTER TABLE tickets_old RENAME TO tickets")

    op.execute("CREATE INDEX ix_tickets_id ON tickets (id)")
    op.execute("CREATE INDEX ix_tickets_title ON tickets (title)")
    op.execute("CREATE INDEX ix_tickets_creator_id ON tickets (creator_id)")
    op.execute("CREATE INDEX ix_tickets_assignee_id ON tickets (assignee_id)")
    op.execute("CREATE INDEX ix_tickets_status ON tickets (status)")
    op.execute("CREATE INDEX ix_tickets_priority ON tickets (priority)")

    op.execute("PRAGMA foreign_keys=ON")
