from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    email_key: Mapped[str] = mapped_column(unique=True)
    recipes: Mapped[list["Recipe"]] = relationship(back_populates="author", passive_deletes="all")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    name_key: Mapped[str] = mapped_column(unique=True)
    recipes: Mapped[list["Recipe"]] = relationship(back_populates="category", passive_deletes="all")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    name_key: Mapped[str] = mapped_column(unique=True)
    recipe_links: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="ingredient", passive_deletes="all"
    )


class Recipe(Base):
    __tablename__ = "recipes"
    __table_args__ = (
        UniqueConstraint("author_id", "title_key"),
        CheckConstraint("prep_time > 0"),
        CheckConstraint("servings > 0"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    title_key: Mapped[str]
    instructions: Mapped[str]
    prep_time: Mapped[int]
    servings: Mapped[int]
    difficulty: Mapped[str] = mapped_column(
        CheckConstraint("difficulty IN ('easy', 'medium', 'hard')"), server_default="easy"
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="RESTRICT"))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    author: Mapped[Author] = relationship(back_populates="recipes")
    category: Mapped[Category | None] = relationship(back_populates="recipes")
    ingredient_links: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe", passive_deletes="all"
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (
        CheckConstraint("quantity > 0"),
        CheckConstraint("unit IN ('g', 'ml', 'pcs')"),
    )

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="RESTRICT"), primary_key=True)
    quantity: Mapped[float]
    unit: Mapped[str]
    recipe: Mapped[Recipe] = relationship(back_populates="ingredient_links")
    ingredient: Mapped[Ingredient] = relationship(back_populates="recipe_links")

