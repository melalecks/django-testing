from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def log_author(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def log_reader(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def homepage_url():
    return reverse('news:home')


@pytest.fixture
def news():
    return News.objects.create(
        title='Название новости',
        text='Текст новости',
        date=datetime.now()
    )


@pytest.fixture
def news_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author
    )


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def create_news():
    current_date = datetime.today()
    some_news = [
        News(title=f'Новость{id}', text='Текст',
             date=current_date - timedelta(days=id))
        for id in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    ]
    News.objects.bulk_create(some_news)


@pytest.fixture
def create_comments(news, author):
    now = datetime.now()
    for id in range(10):
        comment = Comment(text='Текст', news=news, author=author)
        comment.created = now + timedelta(days=id)
        comment.save()


@pytest.fixture
def form_data():
    return {'text': 'Новый текст'}
