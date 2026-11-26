from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

DB = Annotated[Session, Depends(get_db)]


def get_or_404(db, model, key):
    item = db.get(model, key)
    if item is None:
        raise HTTPException(404, f"{model.__name__} not found")
    return item


def save(db, conflict):
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, conflict) from error


def update_fields(item, data):
    values = data.model_dump()
    for field, value in values.items():
        setattr(item, field, value)
        if hasattr(type(item), f"{field}_key"):
            setattr(item, f"{field}_key", value.casefold())


def crud_router(path, model, input_schema, output_schema, unique_message, delete_message):
    router = APIRouter(prefix=path, tags=[path[1:]])

    @router.post("", response_model=output_schema, status_code=201)
    def create(data: input_schema, db: DB):
        item = model()
        update_fields(item, data)
        db.add(item)
        save(db, unique_message)
        return item

    @router.get("", response_model=list[output_schema])
    def list_items(db: DB):
        return db.scalars(select(model).order_by(model.id)).all()

    @router.get("/{item_id}", response_model=output_schema)
    def read(item_id: int, db: DB):
        return get_or_404(db, model, item_id)

    @router.put("/{item_id}", response_model=output_schema)
    def update(item_id: int, data: input_schema, db: DB):
        item = get_or_404(db, model, item_id)
        update_fields(item, data)
        save(db, unique_message)
        return item

    @router.delete("/{item_id}", status_code=204)
    def delete(item_id: int, db: DB):
        db.delete(get_or_404(db, model, item_id))
        save(db, delete_message)
        return Response(status_code=204)

    return router

