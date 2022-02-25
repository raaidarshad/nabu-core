import requests

# these tests expect the API to be running locally
# these tests expect the API to be connected to the dev database


ENDPOINT = "http://127.0.0.1:8000/search"


def test_search_returns_results_if_similar_articles():
    body = {"url": "https://www.foxnews.com/world/russian-invades-ukraine-largest-europe-attack-wwii"}
    response = requests.post(ENDPOINT, json=body)
    assert response.status_code == 200
    assert len(response.json()) != 0


def test_search_returns_empty_if_no_similar_articles():
    body = {"url": "https://www.nytimes.com/live/2022/02/24/world/russia-attacks-ukraine"}
    response = requests.post(ENDPOINT, json=body)
    assert response.status_code == 200
    assert response.json() == []


def test_search_returns_404_if_article_not_found():
    body = {"url": "https://www.fake.com/this/does-not-exist"}
    response = requests.post(ENDPOINT, json=body)
    assert response.status_code == 404
    assert response.json() == {"message": "The submitted URL was not found."}
