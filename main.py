import os
from typing import Annotated

from fastapi import FastAPI, Query, Response
from sqlalchemy import func, select

import models as m
import schemas as s
from crud import DB, crud_router, get_or_404, save, update_fields

app = FastAPI(title="Recipe Catalog API")
MAX_SERVINGS = 50 + int(os.getenv("FACULTY_NUMBER", "00")[-2:])

app.include_router(crud_router(
    "/authors", m.Author, s.AuthorInput, s.AuthorOutput,
    "Email already exists", "Author has recipes",
))
app.include_router(crud_router(
    "/categories", m.Category, s.NameInput, s.NameOutput,
    "Category name already exists", "Category cannot be deleted",
))
app.include_router(crud_router(
    "/ingredients", m.Ingredient, s.NameInput, s.NameOutput,
    "Ingredient name already exists", "Ingredient is used in recipes",
))


@app.get("/authors/{author_id}/recipes", response_model=list[s.RecipeOutput], tags=["authors"])
def author_recipes(author_id: int, db: DB):
    return get_or_404(db, m.Author, author_id).recipes


@app.get("/recipes", response_model=list[s.RecipeOutput], tags=["recipes"])
def list_recipes(
    db: DB,
    title: str | None = None,
    category_id: Annotated[int | None, Query(gt=0)] = None,
    max_prep_time: Annotated[int | None, Query(gt=0)] = None,
):
    query = select(m.Recipe).order_by(m.Recipe.id)
    if title is not None:
        query = query.where(func.instr(m.Recipe.title_key, title.strip().casefold()) > 0)
    if category_id is not None:
        query = query.where(m.Recipe.category_id == category_id)
    if max_prep_time is not None:
        query = query.where(m.Recipe.prep_time <= max_prep_time)
    return db.scalars(query).all()


def save_recipe(db, recipe, data):
    get_or_404(db, m.Author, data.author_id)
    if data.category_id is not None:
        get_or_404(db, m.Category, data.category_id)
    update_fields(recipe, data)
    db.add(recipe)
    save(db, "Recipe title already exists for this author or a reference is no longer valid")
    return recipe


@app.post("/recipes", response_model=s.RecipeOutput, status_code=201, tags=["recipes"])
def create_recipe(data: s.RecipeInput, db: DB):
    return save_recipe(db, m.Recipe(), data)


@app.get("/recipes/{recipe_id}", response_model=s.RecipeOutput, tags=["recipes"])
def read_recipe(recipe_id: int, db: DB):
    return get_or_404(db, m.Recipe, recipe_id)


@app.put("/recipes/{recipe_id}", response_model=s.RecipeOutput, tags=["recipes"])
def update_recipe(recipe_id: int, data: s.RecipeInput, db: DB):
    return save_recipe(db, get_or_404(db, m.Recipe, recipe_id), data)


@app.delete("/recipes/{recipe_id}", status_code=204, tags=["recipes"])
def delete_recipe(recipe_id: int, db: DB):
    db.delete(get_or_404(db, m.Recipe, recipe_id))
    save(db, "Recipe cannot be deleted")
    return Response(status_code=204)


@app.get("/recipes/{recipe_id}/ingredients", response_model=list[s.IngredientLinkOutput], tags=["recipes"])
def recipe_ingredients(recipe_id: int, db: DB):
    return get_or_404(db, m.Recipe, recipe_id).ingredient_links


@app.post("/recipes/{recipe_id}/ingredients", response_model=s.IngredientLinkOutput, status_code=201, tags=["recipes"])
def add_ingredient(recipe_id: int, data: s.IngredientLinkInput, db: DB):
    get_or_404(db, m.Recipe, recipe_id)
    get_or_404(db, m.Ingredient, data.ingredient_id)
    link = m.RecipeIngredient(recipe_id=recipe_id, **data.model_dump())
    db.add(link)
    save(db, "Ingredient already linked to this recipe or a reference is no longer valid")
    return link


@app.put("/recipes/{recipe_id}/ingredients/{ingredient_id}", response_model=s.IngredientLinkOutput, tags=["recipes"])
def update_ingredient(recipe_id: int, ingredient_id: int, data: s.QuantityInput, db: DB):
    link = get_or_404(db, m.RecipeIngredient, (recipe_id, ingredient_id))
    update_fields(link, data)
    save(db, "Ingredient link cannot be updated")
    return link


@app.delete("/recipes/{recipe_id}/ingredients/{ingredient_id}", status_code=204, tags=["recipes"])
def remove_ingredient(recipe_id: int, ingredient_id: int, db: DB):
    db.delete(get_or_404(db, m.RecipeIngredient, (recipe_id, ingredient_id)))
    save(db, "Ingredient link cannot be deleted")
    return Response(status_code=204)


@app.get("/recipes/{recipe_id}/scaled", response_model=s.ScaledRecipe, tags=["recipes"])
def scaled_recipe(recipe_id: int, servings: Annotated[int, Query(gt=0, le=MAX_SERVINGS)], db: DB):
    recipe = get_or_404(db, m.Recipe, recipe_id)
    result = s.RecipeOutput.model_validate(recipe).model_dump()
    result["servings"] = servings
    result["ingredients"] = [
        s.IngredientLinkOutput.model_validate(link).model_copy(
            update={"quantity": link.quantity * (servings / recipe.servings)}
        )
        for link in recipe.ingredient_links
    ]
    return result

