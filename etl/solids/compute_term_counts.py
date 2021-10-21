from dagster import solid
from sklearn.feature_extraction.text import CountVectorizer
import spacy

from etl.common import Context, DagsterTime, get_rows_factory, load_rows_factory, str_to_datetime
from ptbmodels.models import ParsedContent, TermCount


try:
    nlp = spacy.load("en_core_web_sm")
except IOError:
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


get_parsed_content = get_rows_factory("get_parsed_content", ParsedContent)


@solid(config_schema={"runtime": DagsterTime})
def compute_counts(context: Context, parsed_content: list[ParsedContent]) -> list[TermCount]:
    runtime = str_to_datetime(context.solid_config["runtime"])
    count_vectorizer = CountVectorizer(tokenizer=_spacy_tokenizer)
    corpus = [pc.content for pc in parsed_content]

    counts = []

    if corpus:
        count_matrix = count_vectorizer.fit_transform(corpus)
        terms = count_vectorizer.get_feature_names_out()

        for idx, row in enumerate(count_matrix):
            for count, col_index in zip(row.data, row.indices):
                counts.append(TermCount(article_id=parsed_content[idx].article_id,
                                        term=terms[col_index],
                                        count=count,
                                        added_at=runtime
                                        ))

    return counts


load_term_counts = load_rows_factory("load_term_counts", TermCount,
                                     [TermCount.article_id, TermCount.term])


def _spacy_tokenizer(document):
    tokens = nlp(document)
    tokens = [token.lemma_ for token in tokens if (
            not token.is_stop and not token.is_punct and token.lemma_.strip() != ''
            and not token.pos_ == "SYM")]
    return tokens
