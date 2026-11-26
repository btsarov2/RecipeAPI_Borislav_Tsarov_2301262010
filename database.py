from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///./recipes.db", connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def enable_foreign_keys(connection, _):
    connection.execute("PRAGMA foreign_keys = ON")


def get_db():
    with Session(engine) as session:
        yield session

