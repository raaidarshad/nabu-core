from flask import Flask, send_from_directory, request

import feedparser

app = Flask(__name__)


# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('./public', 'index.html')


# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('./public', path)


@app.route("/feed")
def defaultFeed():
    rssUrl = request.args.get("rssUrl")
    limit = int(request.args.get("limit"))
    feed = feedparser.parse(rssUrl)
    feed["entries"] = feed["entries"][:limit]
    return feed


@app.route("/topics")
def get_topic_articles():
    datetime_threshold = request.args.get("threshold")
    # run fn to get topic-grouped articles in desired format


if __name__ == "__main__":
    app.run()
