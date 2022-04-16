import os
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import psycopg
from psycopg.rows import dict_row
from pydantic import BaseModel

from ptbmodels.models import Api


class SearchBody(BaseModel):
    url: str
    limit: Optional[int] = None
    client_id: Optional[str] = None


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


def prepare_url(url: str) -> str:
    without_query_params = url.split("?")[0]
    # percent signs on either side for the postgres "like" text search
    return f"%{without_query_params}%"


def extract_referer(request: Request) -> Optional[str]:
    return request.headers.get("Referer", request.headers.get("Origin"))


# endpoint to submitSearch (lets just call it search)
@app.post("/search")
async def submit_search(search_body: SearchBody, request: Request):
    referer = extract_referer(request)

    async with await psycopg.AsyncConnection.connect(os.getenv("DB_CONNECTION_STRING")) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:
            await acur.execute("SELECT * FROM article WHERE url like %s", (prepare_url(search_body.url), ))
            found_article = await acur.fetchone()
            if found_article:
                await acur.execute("""
                    WITH onedayclusters AS (SELECT *
                        FROM articleclusterlink acl1
                                 JOIN (SELECT * FROM articlecluster WHERE "end" - begin = '1 day') ac1
                                      ON acl1.article_cluster_id = ac1.id)
                
                    SELECT a.url, a.published_at AS date, a.title, s.name AS source
                    FROM article a
                    JOIN source s on s.id = a.source_id
                    JOIN
                    (SELECT DISTINCT onedayclusters.article_id
                    FROM onedayclusters
                    JOIN
                    articleclusterlink a2 ON onedayclusters.article_cluster_id = a2.article_cluster_id
                    WHERE a2.article_id = %(id)s) b ON a.id = b.article_id
                    AND a.id != %(id)s
                    ORDER BY added_at DESC;
                """, found_article)
                rows = await acur.fetchall()

                # TODO this should be replaced with SQLAlchemy "add" type stuff once it works with psycopg3
                log_entry = Api(
                    status_code=200,
                    target_url=search_body.url,
                    client_id=search_body.client_id,
                    referer=referer,
                    response_count=len(rows)
                )
                await acur.execute("""
                INSERT INTO logs.api (timestamp, status_code, target_url, client_id, referer, response_count)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (log_entry.timestamp,
                      log_entry.status_code,
                      log_entry.target_url,
                      log_entry.client_id,
                      log_entry.referer,
                      log_entry.response_count))
                return rows
            else:
                log_entry = Api(
                    status_code=404,
                    target_url=search_body.url,
                    client_id=search_body.client_id,
                    referer=referer
                )
                await acur.execute("""
                INSERT INTO logs.api (timestamp, status_code, target_url, client_id, referer, response_count)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (log_entry.timestamp,
                      log_entry.status_code,
                      log_entry.target_url,
                      log_entry.client_id,
                      log_entry.referer,
                      log_entry.response_count))
                return JSONResponse(status_code=404, content={"message": "The submitted URL was not found."})
