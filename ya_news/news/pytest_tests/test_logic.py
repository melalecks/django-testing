from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


FORM_DATA = {'text': 'Новый текст'}


def test_anonymous_cant_send_comments(client, news_url):
    comments_count = Comment.objects.count()
    client.post(news_url, data=FORM_DATA)
    assert comments_count == Comment.objects.count()


def test_authorised_can_send_comments(log_reader, reader, news, news_url):
    Comment.objects.all().delete()
    log_reader.post(news_url, data=FORM_DATA)
    comment = Comment.objects.get()
    assert 1 == Comment.objects.count()
    assert comment.news == news
    assert comment.author == reader
    assert comment.text == FORM_DATA['text']


def test_author_can_edit(log_author, author, news, edit_url, comment):
    log_author.post(edit_url, FORM_DATA)
    edit_comment = Comment.objects.get(id=comment.id)
    assert edit_comment.news == news
    assert edit_comment.author == author
    assert edit_comment.text == FORM_DATA['text']


def test_author_can_delete(log_author, delete_url):
    count_before_delete = Comment.objects.count()
    response = log_author.delete(delete_url)
    assert Comment.objects.count() == count_before_delete - 1
    assert response.status_code == HTTPStatus.FOUND


def test_reader_cant_edit(log_reader, edit_url, comment):
    response = log_reader.post(edit_url, FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author
    assert comment.text == comment_from_db.text


def test_reader_cant_delete(log_reader, delete_url):
    count_before_delete = Comment.objects.count()
    response = log_reader.delete(delete_url)
    assert Comment.objects.count() == count_before_delete
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_comment_with_bad_words(log_author, news_url):
    FORM_DATA['text'] = BAD_WORDS[0]
    count_before = Comment.objects.count()
    response = log_author.post(news_url, data=FORM_DATA)
    form = response.context['form']
    assert count_before == Comment.objects.count()
    assertFormError(form, 'text', WARNING)
