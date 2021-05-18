import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from etl.db.database import Base
from etl.common import AfAccuracy, AfBias, AllSidesBias, MbfcAccuracy, MbfcBias


class Source(Base):
    __tablename__ = "sources"
    id = Column(UUID, primary_key=True, default=uuid.uuid4, unique=True)
    name = Column(String, nullable=False)
    short_name = Column(String)
    long_name = Column(String)
    rss_url = Column(String, nullable=False)  # TODO make this a constrained type if possible to regex for a valid url
    allsides_bias = Column(Enum(AllSidesBias))
    mbfc_bias = Column(Enum(MbfcBias))
    mbfc_accuracy = Column(Enum(MbfcAccuracy))
    af_bias = Column(Enum(AfBias))
    af_accuracy = Column(Enum(AfAccuracy))


class Article(Base):
    __tablename__ = "articles"
    id = Column(UUID, primary_key=True, default=uuid.uuid4, unique=True)
    url = Column(String, nullable=False)  # TODO make this a constrained type if possible to regex for a valid url
    source_id = Column(UUID, ForeignKey("sources.id"), nullable=False)
    summary = Column(String)
    title = Column(String)
    raw_content = Column(JSON)
    parsed_content = Column(String)
    published_at = Column(DateTime, nullable=False)
    # authors = Column() TODO figure out a good way to do this; will be captured in raw_content

    # many to one
    source = relationship("Source", foreign_keys=[source_id])
