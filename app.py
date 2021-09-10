from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from flask import Flask, send_from_directory, request
import feedparser

# from etl.functions import clusterify, compute_similarity_data, get_count_data, prep_clusters


app = FastAPI()


# Path for our main Svelte page
# @app.get("/")
# def base():
#     return send_from_directory('./public', 'index.html')


# Path for all the static files (compiled JS/CSS, etc.)
# @app.get("/{path}")
# def home(path):
#     return send_from_directory('./public', path)

app.mount("/public", StaticFiles(directory="public"), name="public")


# @app.get("/feed")
# def defaultFeed():
#     rssUrl = request.args.get("rssUrl")
#     limit = int(request.args.get("limit"))
#     feed = feedparser.parse(rssUrl)
#     feed["entries"] = feed["entries"][:limit]
#     return feed


# @app.get("/clusters")
# def clusters():
#     datetime_threshold = datetime.now(tz=timezone.utc) - timedelta(days=1)
#     filter_threshold = 0.45
#
#     count_data = get_count_data(datetime_threshold, db_client)
#     similarity_data = compute_similarity_data(count_data, filter_threshold)
#     raw_clusters = clusterify(similarity_data.similarity_matrix)
#     prep_clusters(raw_clusters, similarity_data)
