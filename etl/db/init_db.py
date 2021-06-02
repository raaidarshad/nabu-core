import json

from sqlalchemy.orm.session import Session

from etl.db.database import DbSession, engine
from etl.db.models import Source as DbSource, Base
from etl.models import Source


def load_sources_from_file():
    # get db session
    db: Session = DbSession()
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
    db_sources = [DbSource(**src) for src in sources]
    db.add_all(db_sources)
    db.commit()


def _get_sources(db: Session):
    return db.query(DbSource).all()


def update_sources():
    pass


if __name__ == "__main__":
    # create tables
    Base.metadata.create_all(bind=engine)
    # initialize sources
    load_sources_from_file()
    # # run pipeline to set source accuracies and biases
    update_sources()
