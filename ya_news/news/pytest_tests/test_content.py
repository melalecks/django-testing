import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_amount_of_news(client, homepage_url, create_news):
    response = client.get(homepage_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_sorting_of_news(client, homepage_url, create_news):
    response = client.get(homepage_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_sorting_of_comments(client, news_url, create_comments):
    response = client.get(news_url)
    news_detail = response.context['news']
    comments = news_detail.comment_set.all()
    all_dates = [comment.created for comment in comments]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comment_form_unavailable_for_anonymous(client, news_url):
    assert 'form' not in client.get(news_url).context


@pytest.mark.django_db
def test_comment_form_available_for_authorised(log_reader, news_url):
    response = log_reader.get(news_url).context
    assert 'form' in response
    form = response['form']
    assert isinstance(form, CommentForm)
