from etl.db.database import Base, engine


def load_sources_from_file():
    pass


def update_sources():
    pass


if __name__ == "__main__":
    # create tables
    Base.metadata.create_all(bind=engine)
    # initialize sources
    load_sources_from_file()
    # run pipeline to set source accuracies and biases
    update_sources()
