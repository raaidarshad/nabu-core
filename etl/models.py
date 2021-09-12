from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, HttpUrl
from sqlmodel import Column, Enum, Field, JSON, Relationship, String, SQLModel

from etl.common import AfAccuracy, AfBias, AsBias, MbfcAccuracy, MbfcBias


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
        orm_mode = True
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

    class Config:
        orm_mode = True


class TermCount(SQLModel, table=True):
    article_id: UUID = Field(foreign_key="article.id", primary_key=True, index=True)
    term: str = Field(index=True, primary_key=True)
    count: int = Field(primary_key=True)

    article: Article = Relationship(back_populates="term_counts")

    class Config:
        orm_mode = True
