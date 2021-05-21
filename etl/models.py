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
    published_at: datetime = Field(alias="published")
    url: HttpUrl = Field(alias="link")
    authors: str = Field(alias="author")


class Feed(BaseModel):
    title: str
    subtitle: Optional[str]
    entries: list[FeedEntry]
    url: HttpUrl = Field(alias="link")
    updated_at: datetime = Field(alias="updated")


class Article(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    url: HttpUrl
    source_id: UUID
    summary: Optional[str]
    title: str
    raw_content: str  # JSON?
    parsed_content: Optional[str]
    published_at: datetime
    authors: str

    class Config:
        orm_mode = True
