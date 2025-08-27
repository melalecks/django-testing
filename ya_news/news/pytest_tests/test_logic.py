from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_cant_send_comments(client, news_url, form_data):
    comments_count = Comment.objects.count()
    client.post(news_url, data=form_data)
    assert comments_count == Comment.objects.count()


def test_authorised_can_send_comments(log_reader, reader, news, news_url,
                                      form_data):
    comments_count = Comment.objects.count()
    log_reader.post(news_url, data=form_data)
    assert comments_count + 1 == Comment.objects.count()
    assert (
        Comment.objects.latest('id').news,
        Comment.objects.latest('id').author,
        Comment.objects.latest('id').text
    ) == (news, reader, form_data['text'])


def test_author_can_edit(log_author, author, news, edit_url, form_data,
                         comment):
    log_author.post(edit_url, form_data)
    comment.refresh_from_db()
    assert (
        comment.news,
        comment.author,
        comment.text
    ) == (news, author, form_data['text'])


def test_author_can_delete(log_author, delete_url):
    count_before_delete = Comment.objects.count()
    response = log_author.delete(delete_url)
    assert Comment.objects.count() == count_before_delete - 1
    assert response.status_code == HTTPStatus.FOUND


def test_reader_cant_edit(log_reader, edit_url, form_data,
                          comment):
    response = log_reader.post(edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert (
        comment.news,
        comment.author,
        comment.text
    ) == (comment_from_db.news, comment_from_db.author, comment_from_db.text)


def test_reader_cant_delete(log_reader, delete_url):
    count_before_delete = Comment.objects.count()
    response = log_reader.delete(delete_url)
    assert Comment.objects.count() == count_before_delete
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_comment_with_bad_words(log_author, form_data, news_url):
    form_data['text'] = BAD_WORDS[0]
    count_before = Comment.objects.count()
    response = log_author.post(news_url, data=form_data)
    form = response.context['form']
    assertFormError(form, 'text', WARNING)
    assert count_before == Comment.objects.count()
