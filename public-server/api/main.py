import os
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import psycopg
from psycopg.rows import dict_row
from pydantic import BaseModel


class SearchBody(BaseModel):
    url: str
    limit: Optional[int] = None


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# endpoint to submitSearch (lets just call it search)
@app.post("/search")
async def submit_search(search_body: SearchBody):
    # if the url is not found, return a 404 code
    # if the url is found but no similar articles, return a 200 with an empty body
    # if the url is found and there are similar articles, return a 200 and a full body
    async with await psycopg.AsyncConnection.connect(os.getenv("DB_CONNECTION_STRING")) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:
            await acur.execute("SELECT * FROM article WHERE url ilike %s", (search_body.url, ))
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
                return rows
            else:
                return JSONResponse(status_code=404, content={"message": "The submitted URL was not found."})
