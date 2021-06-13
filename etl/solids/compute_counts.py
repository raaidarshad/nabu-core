import datetime

from dagster import Output, OutputDefinition, String, solid
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import CountVectorizer
import spacy
from sqlalchemy.orm import Session

from etl.common import Context
from etl.db.models import Article as DbArticle, Count as DbCount
from etl.models import Article, Count

nlp = spacy.load("en_core_web_lg")


@solid(required_resource_keys={"database_client"}, config_schema={"time_threshold": String})
def get_articles(context: Context) -> list[Article]:
    db_client: Session = context.resources.database_client
    time_threshold_str = context.solid_config["time_threshold"]
    time_threshold = datetime.datetime.strptime(time_threshold_str, "%Y-%m-%d %H:%M:%S.%f%z")

    # filter to articles published after time threshold
    # left join, then
    # get articles with ids NOT in counts
    articles = db_client.query(DbArticle).\
        filter(DbArticle.published_at >= time_threshold).\
        outerjoin(DbCount.article_id).\
        filter(DbCount.article_id.is_(None)).all()

    context.log.info(f"Got {len(articles)} articles")
    return [Article(**a.__dict__) for a in articles]


@solid(output_defs=[
    OutputDefinition(name="count_matrix"),
    OutputDefinition(name="features")
])
def compute_count_matrix(_context: Context, articles: list[Article]):
    count_vectorizer = CountVectorizer(tokenizer=_spacy_tokenizer)
    corpus = [article.parsed_content for article in articles]
    count_matrix = count_vectorizer.fit_transform(corpus)
    features = count_vectorizer.get_feature_names()
    yield Output(count_matrix, "count_matrix")
    yield Output(features, "features")


@solid
def compose_rows(_context: Context,
                 articles: list[Article],
                 features: list[str],
                 count_matrix: csr_matrix) -> list[Count]:
    assert len(articles) == count_matrix.shape[0], "Number of articles != number of rows in count_matrix"

    counts = []

    for idx in range(count_matrix.shape[0]):
        current_indices = count_matrix.getrow(idx).indices
        current_data = count_matrix.getrow(idx).data
        for jdx in range(current_indices):
            counts.append(
                Count(article_id=articles[idx].id, term=features[current_indices[jdx]], count=current_data[jdx]))

    return counts


@solid(required_resource_keys={"database_client"})
def load_counts(context: Context, counts: list[Count]):
    db_client: Session = context.resources.database_client
    db_client.add_all([DbCount(**count.dict()) for count in counts])
    db_client.commit()


def _spacy_tokenizer(document):
    tokens = nlp(document)
    tokens = [token.lemma_ for token in tokens if (
            not token.is_stop and not token.is_punct and token.lemma_.strip() != '')]
    return tokens
