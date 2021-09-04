from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, HttpUrl
from sqlmodel import Enum, Field, SQLModel

from etl.common import AfAccuracy, AfBias, AsBias, MbfcAccuracy, MbfcBias


class Source(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(nullable=False)
    short_name: str
    long_name: str
    rss_url: str = Field(nullable=False)
    html_parser_config: dict = Field(nullable=False)
    allsides_bias: Optional[Enum[AsBias]]
    mbfc_bias: Optional[Enum[MbfcBias]]
    mbfc_accuracy: Optional[Enum[MbfcAccuracy]]
    af_bias: Optional[Enum[AfBias]]
    af_accuracy: Optional[Enum[AfAccuracy]]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


# class Source(BaseModel):
#     id: UUID = Field(default_factory=uuid4)
#     name: str
#     short_name: Optional[str]
#     long_name: Optional[str]
#     rss_url: HttpUrl
#     html_parser_config: dict
#     allsides_bias: Optional[AsBias]
#     mbfc_bias: Optional[MbfcBias]
#     mbfc_accuracy: Optional[MbfcAccuracy]
#     af_bias: Optional[AfBias]
#     af_accuracy: Optional[AfAccuracy]
#
#     class Config:
#         orm_mode = True


class FeedEntry(BaseModel):
    title: str
    summary: str
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
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    url: HttpUrl = Field(nullable=False)
    source_id: UUID = Field(foreign_key="source.id", nullable=False)
    summary: Optional[str]
    title: str
    parsed_content: Optional[str]
    published_at: datetime = Field(nullable=False, index=True)
    authors: Optional[str]

    class Config:
        orm_mode = True


class Count(SQLModel, table=True):
    article_id: UUID = Field(foreign_key="article.id", primary_key=True, index=True, nullable=False)
    term: str = Field(index=True, nullable=False)
    count: int = Field(nullable=False)

    class Config:
        orm_mode = True
