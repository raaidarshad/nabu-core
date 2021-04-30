import concurrent.futures
from functools import partial
import logging
import threading

import time

import feedparser
import numpy as np
import pandas
import pandas as pd
import requests_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import spacy

from pipelines.common import Article, ArticleCluster, Cluster, Feed, Lean, TaggedCluster, Tags, headers, urls_and_leans

logging.basicConfig(filename="statsSession.log",
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
thread_local = threading.local()
nlp = spacy.load("en_core_web_lg")


def get_session():
    if not hasattr(thread_local, "session"):
        session = requests_cache.CachedSession()
        session.headers = headers
        thread_local.session = session
    return thread_local.session


def get_feed(url: str, lean: Lean, limit: int = 10) -> Feed:
    feed = feedparser.parse(url)
    feed["entries"] = feed["entries"][:limit]
    return Feed(lean=lean, content=feed, url=url)


# @task
def feeds_to_articles(feeds: list[Feed]) -> list[Article]:

    def parse_content(entry, feed: Feed) -> Article:
        try:
            with get_session().get(entry.link) as response:
                text = feed.html_parser.extract(content=response.content)
        except:
            logging.info(f"Article with URL {entry.link} was not parsed successfully")
            text = entry.summary
        return Article(id=entry.link, source=feed.content.url, entry=entry, content=text)

    articles = []

    for feed in feeds:
        current_parse = partial(parse_content, feed=feed)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            texts = executor.map(current_parse, feed.content.entries)
            articles.extend(texts)
    return articles


def spacy_tokenizer(document):
    tokens = nlp(document)
    tokens = [token.lemma_ for token in tokens if (
            not token.is_stop and not token.is_punct and token.lemma_.strip() != '')]
    return tokens


def compute_similarity(articles: list[Article]):
    tfidf_vectorizer = TfidfVectorizer(input="content", tokenizer=spacy_tokenizer)
    corpus = [article.content for article in articles]
    result = tfidf_vectorizer.fit_transform(corpus)
    logging.info(f"TF-IDF vectorizer complete: {time.time() - start_time}")
    cos_df = pd.DataFrame(columns=list(range(result.shape[0])))
    for i in range(result.shape[0]):
        curr_cos_sim = linear_kernel(result[i], result).flatten()
        cos_df[i] = curr_cos_sim

    return cos_df


def saturate_data(df: pandas.DataFrame, threshold: float = 0.2) -> pandas.DataFrame:
    def saturate(val: float) -> bool:
        return val > threshold

    return df.apply(np.vectorize(saturate))


def clusterify(df: pandas.DataFrame) -> set[Cluster]:
    # df with unique rows
    deduped = df.drop_duplicates()
    # get indexed rows instead of boolean rows
    clusters = []
    for idx, row in deduped.iterrows():
        clusters.append(set(deduped.columns[row].values))

    # merge sets that have overlap
    merged_clusters = []
    for idx, cluster in enumerate(clusters):
        current = cluster
        for comp in clusters:
            # option 1
            if current.intersection(comp):
            # option 2
            # if len(current.intersection(comp)) > len(comp.difference(current)):
                current = current.union(comp)
        merged_clusters.append(current)
        clusters[idx] = current

    # dedupe merged sets
    return set([frozenset(s) for s in merged_clusters])


def clusters_to_article_clusters(clusters: set[Cluster], articles: list[Article]) -> set[ArticleCluster]:
    article_clusters = []
    for cluster in clusters:
        article_clusters.append(frozenset([articles[idx] for idx in cluster]))

    return set(article_clusters)


def compute_tags(cluster: Cluster) -> Tags:
    # TODO might need the original sparse matrix that shows what terms things were related on?
    pass


def tagify(cluster: Cluster) -> TaggedCluster:
    pass


start_time = time.time()

feeds = [get_feed(url, lean, limit=20) for url, lean in urls_and_leans]
logging.info(f"Feeds obtained: {time.time() - start_time}")
articles = feeds_to_articles(feeds=feeds)
logging.info(f"Articles obtained: {time.time() - start_time}")
sim_df = compute_similarity(articles)
logging.info(f"Similarity df computed: {time.time() - start_time}")
sat_df = saturate_data(sim_df, threshold=0.45)
logging.info(f"Dataframe saturated: {time.time() - start_time}")
clusters = clusterify(sat_df)
logging.info(f"Clusters identified: {time.time() - start_time}")
article_clusters = clusters_to_article_clusters(clusters, articles)
logging.info(f"Article clusters obtained: {time.time() - start_time}")
logging.info(f"There are {len(article_clusters)} clusters and {len(articles)} articles")
clusters_bigger_than_1 = 0
for merp in article_clusters:
    if len(merp) > 1:
        clusters_bigger_than_1 += 1
        for flerp in merp:
            print(f"{flerp.source}: {flerp.entry.title}")
        print("- - - - - -")

logging.info(f"There are {clusters_bigger_than_1} clusters with more than 1 article")
# tagged_clusters = [tagify(cluster) for cluster in clusters]

# okay so new pipeline approach works better, lets see how to clean this up

# 1. get feed urls
# 2. get feeds as dicts || medium gains here, http requests, I/O bound
# 3. tokenize articles || big gains here, http requests and html parsing probably not the fastest, mostly I/O bound
# 4. fit_transform with tf-idf
# 5. calculate similarities between articles
# 6. create groups (cluster) based off of similarities
# 7. label groups (tag)
# 8. present groups
