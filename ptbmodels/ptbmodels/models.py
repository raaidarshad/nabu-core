from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, HttpUrl
from sqlmodel import Column, Field, Index, JSON, Relationship, String, SQLModel, func

from enum import Enum


###############################
### BIAS AND ACCURACY ENUMS ###
###############################


class MbfcBias(Enum):
    LEAST_BIASED = "LEAST_BIASED"
    LEFT_CENTER = "LEFT_CENTER"
    RIGHT_CENTER = "RIGHT_CENTER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    FAR_LEFT = "FAR_LEFT"
    FAR_RIGHT = "FAR_RIGHT"


class AfBias(Enum):
    MIDDLE = "MIDDLE"
    SKEWS_LEFT = "SKEWS_LEFT"
    SKEWS_RIGHT = "SKEWS_RIGHT"
    HYPER_PARTISAN_LEFT = "HYPER_PARTISAN_LEFT"
    HYPER_PARTISAN_RIGHT = "HYPER_PARTISAN_RIGHT"
    MOST_EXTREME_LEFT = "MOST_EXTREME_LEFT"
    MOST_EXTREME_RIGHT = "MOST_EXTREME_RIGHT"


class AsBias(Enum):
    LEFT = "LEFT"
    LEAN_LEFT = "LEAN_LEFT"
    CENTER = "CENTER"
    LEAN_RIGHT = "LEAN_RIGHT"
    RIGHT = "RIGHT"


class BiasTypes(Enum):
    # media bias fact check
    MBFC = "MBFC"
    # ad fontes
    AF = "AF"
    # all sides
    AS = "AS"


class MbfcAccuracy(Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MIXED = "MIXED"
    MOSTLY_FACTUAL = "MOSTLY_FACTUAL"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class AfAccuracy(Enum):
    pass


class AccuracyTypes(Enum):
    MBFC = "MBFC"


#######################
### INTERNAL MODELS ###
#######################


class RawFeedEntry(BaseModel):
    title: str
    summary: Optional[str]
    published_at: datetime
    url: HttpUrl = Field(alias="link")
    authors: Optional[str] = Field(alias="author")
    rss_feed_id: UUID
    source_id: int


class RawFeed(BaseModel):
    title: str
    entries: list[RawFeedEntry]
    url: HttpUrl = Field(alias="link")
    rss_feed_id: UUID
    source_id: int


#########################
### TABLE DEFINITIONS ###
#########################

class PTBModel(SQLModel):
    pass


class PTBTagModel(PTBModel):
    added_at: datetime


class ArticleClusterLink(SQLModel, table=True):
    article_cluster_id: Optional[UUID] = Field(default=None, foreign_key="articlecluster.id", primary_key=True)
    article_id: Optional[UUID] = Field(default=None, foreign_key="article.id", primary_key=True)


class Source(PTBModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(sa_column=Column(String, unique=True))

    biases: List["Bias"] = Relationship(back_populates="source")
    accuracies: List["Accuracy"] = Relationship(back_populates="source")
    rss_feeds: List["RssFeed"] = Relationship(back_populates="source")


class Bias(PTBModel, table=True):
    source_id: int = Field(foreign_key="source.id", primary_key=True)
    # TODO enum?
    type: str = Field(primary_key=True)
    value: str

    source: Source = Relationship(back_populates="biases")


class Accuracy(PTBModel, table=True):
    source_id: int = Field(foreign_key="source.id", primary_key=True)
    # TODO enum?
    type: str = Field(primary_key=True)
    value: str

    source: Source = Relationship(back_populates="accuracies")


class RssFeed(PTBModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    source_id: int = Field(foreign_key="source.id")
    url: HttpUrl = Field(sa_column=Column(String, unique=True))
    parser_config: dict = Field(sa_column=Column(JSON))
    # whether or not the http status code was 2XX on the most recent test
    is_okay: bool = Field(default=True)

    source: Source = Relationship(back_populates="rss_feeds")


class Article(PTBTagModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    rss_feed_id: Optional[UUID] = Field(foreign_key="rssfeed.id")
    source_id: int = Field(foreign_key="source.id")
    url: HttpUrl = Field(sa_column=Column(String, unique=True))
    summary: str = Field(index=False)
    title: str = Field(index=False)
    authors: Optional[str] = Field(index=False)
    published_at: datetime

    rss_feed: RssFeed = Relationship()
    source: Source = Relationship()
    term_counts: List["TermCount"] = Relationship(back_populates="article")
    clusters: List["ArticleCluster"] = Relationship(back_populates="articles", link_model=ArticleClusterLink)
    raw_content: "RawContent" = Relationship(back_populates="article")
    parsed_content: "ParsedContent" = Relationship(back_populates="article")


Index("ix_article_title", func.to_tsvector('english', Article.title), postgresql_using="gin")
Index("ix_article_summary", func.to_tsvector('english', Article.summary), postgresql_using="gin")
Index("ix_article_authors", func.to_tsvector('english', Article.authors), postgresql_using="gin")


class RawContent(PTBTagModel, table=True):
    article_id: UUID = Field(foreign_key="article.id", primary_key=True)
    content: str = Field(index=False)

    article: Article = Relationship(back_populates="raw_content")


Index("ix_rawcontent_content", func.to_tsvector('english', RawContent.content), postgresql_using="gin")


class ParsedContent(PTBTagModel, table=True):
    article_id: UUID = Field(foreign_key="article.id", primary_key=True)
    content: str = Field(index=False)

    article: Article = Relationship(back_populates="parsed_content")


Index("ix_parsedcontent_content", func.to_tsvector('english', RawContent.content), postgresql_using="gin")


class TermCount(PTBTagModel, table=True):
    article_id: UUID = Field(foreign_key="article.id", primary_key=True)
    term: str = Field(primary_key=True)
    count: int = Field(primary_key=True)

    article: Article = Relationship(back_populates="term_counts")


class ArticleCluster(PTBTagModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    # TODO enum? might be more trouble than it is worth
    type: str
    parameters: dict = Field(sa_column=Column(JSON))
    # range of time that this cluster goes over, i.e. 1440 for a day
    minute_span: int

    articles: List[Article] = Relationship(back_populates="clusters", link_model=ArticleClusterLink)
