from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, PositiveInt, StringConstraints

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Input(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class NameInput(Input):
    name: Text


class NameOutput(NameInput):
    id: int


class AuthorInput(NameInput):
    email: EmailStr


class AuthorOutput(AuthorInput):
    id: int


class RecipeInput(Input):
    title: Text
    instructions: Text
    prep_time: PositiveInt
    servings: PositiveInt
    difficulty: Literal["easy", "medium", "hard"]
    author_id: PositiveInt
    category_id: PositiveInt | None = None


class RecipeOutput(RecipeInput):
    id: int


class QuantityInput(Input):
    quantity: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    unit: Literal["g", "ml", "pcs"]


class IngredientLinkInput(QuantityInput):
    ingredient_id: PositiveInt


class IngredientLinkOutput(IngredientLinkInput):
    ingredient: NameOutput


class ScaledRecipe(RecipeOutput):
    ingredients: list[IngredientLinkOutput]

