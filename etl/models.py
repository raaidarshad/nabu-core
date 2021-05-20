from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, HttpUrl

from etl.common import AfAccuracy, AfBias, AsBias, MbfcAccuracy, MbfcBias


class Source(BaseModel):
    id: UUID = uuid4()
    name: str
    short_name: Optional[str]
    long_name: Optional[str]
    rss_url: HttpUrl
    allsides_bias: Optional[AsBias]
    mbfc_bias: Optional[MbfcBias]
    mbfc_accuracy: Optional[MbfcAccuracy]
    af_bias: Optional[AfBias]
    af_accuracy: Optional[AfAccuracy]


class FeedEntry(BaseModel):
    title: str
    summary: str
    published: datetime
    url: HttpUrl  # TODO "link"
    authors: str  # TODO .author (without s) contains just the value from ^; might be better to use that


class Feed(BaseModel):
    title: str
    subtitle: Optional[str]
    entries: list[FeedEntry]
    url: HttpUrl  # TODO "link"
    updated: datetime


class Article(BaseModel):
    id: UUID = uuid4()
    url: HttpUrl
    source_id: UUID
    summary: Optional[str]
    title: str
    raw_content: str  # JSON?
    parsed_content: Optional[str]
    published_at: datetime
    authors: str
