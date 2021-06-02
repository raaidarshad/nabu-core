from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl

from etl.common import AfAccuracy, AfBias, AsBias, MbfcAccuracy, MbfcBias


class Source(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    short_name: Optional[str]
    long_name: Optional[str]
    rss_url: HttpUrl
    html_parser_config: dict
    allsides_bias: Optional[AsBias]
    mbfc_bias: Optional[MbfcBias]
    mbfc_accuracy: Optional[MbfcAccuracy]
    af_bias: Optional[AfBias]
    af_accuracy: Optional[AfAccuracy]

    class Config:
        orm_mode = True


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


class Article(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    url: HttpUrl
    source_id: UUID
    summary: Optional[str]
    title: str
    parsed_content: Optional[str]
    published_at: datetime
    authors: Optional[str]

    class Config:
        orm_mode = True
