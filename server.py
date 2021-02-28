from flask import Flask, send_from_directory, request
import random
import requests

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
def hello():
    rssUrl = request.args.get('rssUrl')
    limit = int(request.args.get('limit'))
    feed = feedparser.parse(rssUrl)
    feed["entries"] = feed["entries"][:limit]
    return feed


if __name__ == "__main__":
    app.run(debug=True)