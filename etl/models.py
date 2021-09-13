from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, HttpUrl
from sqlmodel import ARRAY, Column, Enum, Field, JSON, Relationship, String, SQLModel

from etl.common import AfAccuracy, AfBias, AsBias, MbfcAccuracy, MbfcBias


class ClusterToLink(SQLModel, table=True):
    cluster_id: Optional[UUID] = Field(default=None, foreign_key="cluster.id", primary_key=True)
    article_id: Optional[UUID] = Field(default=None, foreign_key="article.id", primary_key=True)


class Source(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str
    short_name: Optional[str]
    long_name: Optional[str]
    rss_url: str = Field(sa_column=Column(String, unique=True))
    html_parser_config: dict = Field(sa_column=Column(JSON))
    allsides_bias: Optional[AsBias] = Field(sa_column=Column(Enum(AsBias)))
    mbfc_bias: Optional[MbfcBias] = Field(sa_column=Column(Enum(MbfcBias)))
    mbfc_accuracy: Optional[MbfcAccuracy] = Field(sa_column=Column(Enum(MbfcAccuracy)))
    af_bias: Optional[AfBias] = Field(sa_column=Column(Enum(AfBias)))
    af_accuracy: Optional[AfAccuracy] = Field(sa_column=Column(Enum(AfAccuracy)))

    class Config:
        arbitrary_types_allowed = True


class FeedEntry(BaseModel):
    title: str
    summary: Optional[str]
    published_at: datetime
    url: HttpUrl = Field(alias="link")
    authors: Optional[str] = Field(alias="author")
    source_id: UUID


class Feed(BaseModel):
    title: str
    subtitle: Optional[str]
    entries: list[FeedEntry]
    url: HttpUrl = Field(alias="link")
    updated_at: datetime
    source_id: UUID


class Article(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, index=True)
    url: HttpUrl = Field(nullable=False, sa_column=Field(String, sa_column=Column(unique=True)))
    source_id: UUID = Field(foreign_key="source.id")
    summary: Optional[str] = Field(index=False)  # TODO remove this Field statement
    title: str
    parsed_content: Optional[str] = Field(index=False)  # TODO remove this Field statement
    published_at: datetime = Field(index=True)
    authors: Optional[str]

    source: Source = Relationship()
    term_counts: List["TermCount"] = Relationship(back_populates="article")
    clusters: List["Cluster"] = Relationship(back_populates="articles", link_model=ClusterToLink)

    class Config:
        arbitrary_types_allowed = True


class TermCount(SQLModel, table=True):
    article_id: UUID = Field(foreign_key="article.id", primary_key=True, index=True)
    term: str = Field(index=True, primary_key=True)
    count: int = Field(primary_key=True)

    article: Article = Relationship(back_populates="term_counts")


class Cluster(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, index=True)
    keywords: list[str] = Field(sa_column=Column(ARRAY(String)))
    computed_at: datetime = Field(index=True)
    # dayspan is the span of minutes that this cluster covers, so 60 is 1 hour, 1440 is a day, etc.
    minute_span: int = Field(index=True)

    articles: List[Article] = Relationship(back_populates="clusters", link_model=ClusterToLink)
