import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade():
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("email_key", sa.String, nullable=False, unique=True),
    )
    for table in ("categories", "ingredients"):
        op.create_table(
            table,
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("name", sa.String, nullable=False),
            sa.Column("name_key", sa.String, nullable=False, unique=True),
        )
    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("title_key", sa.String, nullable=False),
        sa.Column("instructions", sa.String, nullable=False),
        sa.Column("prep_time", sa.Integer, nullable=False),
        sa.Column("servings", sa.Integer, nullable=False),
        sa.Column("author_id", sa.Integer, sa.ForeignKey("authors.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id", ondelete="SET NULL")),
        sa.UniqueConstraint("author_id", "title_key"),
        sa.CheckConstraint("prep_time > 0"),
        sa.CheckConstraint("servings > 0"),
    )
    op.create_table(
        "recipe_ingredients",
        sa.Column("recipe_id", sa.Integer, sa.ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("ingredient_id", sa.Integer, sa.ForeignKey("ingredients.id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("quantity", sa.Float, nullable=False),
        sa.Column("unit", sa.String, nullable=False),
        sa.CheckConstraint("quantity > 0"),
        sa.CheckConstraint("unit IN ('g', 'ml', 'pcs')"),
    )


def downgrade():
    for table in ("recipe_ingredients", "recipes", "ingredients", "categories", "authors"):
        op.drop_table(table)

