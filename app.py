from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import feedparser

# from etl.functions.clusters import clusterify, prep_clusters
# from etl.functions.counts import get_count_data
# from etl.functions.tfidf import compute_similarity_data


app = FastAPI()


@app.get("/feed")
def defaultFeed(rssUrl: str, limit: int):
    feed = feedparser.parse(rssUrl)
    feed["entries"] = feed["entries"][:limit]
    return feed


# Path for all the static files (compiled JS/CSS, index.html, etc.)
app.mount("/", StaticFiles(directory="public", html=True), name="public")


# @app.get("/clusters")
# def clusters():
#     datetime_threshold = datetime.now(tz=timezone.utc) - timedelta(days=1)
#     filter_threshold = 0.45
#
#     count_data = get_count_data(datetime_threshold, db_client)
#     similarity_data = compute_similarity_data(count_data, filter_threshold)
#     raw_clusters = clusterify(similarity_data.similarity_matrix)
#     prep_clusters(raw_clusters, similarity_data)
