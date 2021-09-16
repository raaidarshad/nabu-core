from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import feedparser


app = FastAPI()


@app.get("/feed")
def defaultFeed(rssUrl: str, limit: int):
    feed = feedparser.parse(rssUrl)
    feed["entries"] = feed["entries"][:limit]
    return feed


# Path for all the static files (compiled JS/CSS, index.html, etc.)
app.mount("/", StaticFiles(directory="public", html=True), name="public")
