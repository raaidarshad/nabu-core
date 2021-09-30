import os

from sqlmodel import create_engine

from ptbmodels.models import SQLModel


def test_create_tables():
    # if it runs and no errors pop up, congrats, the tables were made successfully
    db_engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
    SQLModel.metadata.create_all(db_engine)
