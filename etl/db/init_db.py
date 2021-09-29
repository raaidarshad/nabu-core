import os
import json

from sqlmodel import Session, SQLModel, create_engine

from ptbmodels.models import Source


engine = create_engine(os.getenv("DB_CONNECTION_STRING"))


def get_session():
    return Session(engine, autocommit=False, autoflush=False)


def load_sources_from_file():
    # get db session
    db: Session = get_session()
    # load json file
    raw_sources = _load_json(filepath="sources.json")
    # write to db
    _write_sources(db=db, sources=raw_sources)
    # print to see if it worked
    from_db = _get_sources(db=db)
    a = [Source(**s.__dict__) for s in from_db]
    print(a)


def _load_json(filepath: str) -> list[dict]:
    with open(filepath, "r") as data:
        return json.load(data)


def _write_sources(db: Session, sources: list[dict]):
    db_sources = [Source(**src) for src in sources]
    db.add_all(db_sources)
    db.commit()


def _get_sources(db: Session):
    return db.query(Source).all()


def update_sources():
    pass


if __name__ == "__main__":
    # create tables
    SQLModel.metadata.create_all(engine)
    # initialize sources
    load_sources_from_file()
    # # run pipeline to set source accuracies and biases
    update_sources()
