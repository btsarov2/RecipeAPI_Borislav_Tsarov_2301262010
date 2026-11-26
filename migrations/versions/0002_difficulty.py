import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"


def upgrade():
    op.add_column(
        "recipes",
        sa.Column(
            "difficulty",
            sa.String,
            sa.CheckConstraint("difficulty IN ('easy', 'medium', 'hard')"),
            nullable=False,
            server_default="easy",
        ),
    )


def downgrade():
    op.drop_column("recipes", "difficulty")
