"""
Pipeline that takes FeedData as input and outputs Articles. The input comes from constants, and the output
goes to a Postgres DB.

IOManagers
1. FeedData input
2. Article dataset output

Solids
1. get_feeds: <input> -> Feeds
    2. get_feed: url, limit -> Feed
3. feed_to_articles: Feed -> Articles
    4. feed_to_entry: Feed -> Entry
    5. parse_article: Entry -> Article
"""

