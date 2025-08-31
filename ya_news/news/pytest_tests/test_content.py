import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_amount_of_news(client, homepage_url, create_news):
    assert client.get(homepage_url).context['object_list'].count(
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_sorting_of_news(client, homepage_url, create_news):
    response = client.get(homepage_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_sorting_of_comments(client, news_url, create_comments):
    response = client.get(news_url)
    news_detail = response.context['news']
    comments = news_detail.comment_set.all()
    all_dates = [comment.created for comment in comments]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


def test_comment_form_unavailable_for_anonymous(client, news_url):
    assert 'form' not in client.get(news_url).context


def test_comment_form_available_for_authorised(log_reader, news_url):
    response_context = log_reader.get(news_url).context
    assert 'form' in response_context
    assert isinstance(response_context['form'], CommentForm)
