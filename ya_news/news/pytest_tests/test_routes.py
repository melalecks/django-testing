from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize('parametrized_client, url, method, status', (
        (pytest.lazy_fixture('client'), pytest.lazy_fixture('login_url'),
         'get', HTTPStatus.OK),
        (pytest.lazy_fixture('client'), pytest.lazy_fixture('logout_url'),
         'post', HTTPStatus.OK),
        (pytest.lazy_fixture('client'), pytest.lazy_fixture('signup_url'),
         'get', HTTPStatus.OK),
        (pytest.lazy_fixture('client'), pytest.lazy_fixture('homepage_url'),
         'get', HTTPStatus.OK),
        (pytest.lazy_fixture('client'), pytest.lazy_fixture('news_url'),
         'get', HTTPStatus.OK),
        (pytest.lazy_fixture('log_author'), pytest.lazy_fixture('edit_url'),
         'get', HTTPStatus.OK),
        (pytest.lazy_fixture('log_author'), pytest.lazy_fixture('delete_url'),
         'get', HTTPStatus.OK),
        (pytest.lazy_fixture('log_reader'), pytest.lazy_fixture('edit_url'),
         'get', HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('log_reader'), pytest.lazy_fixture('delete_url'),
         'get', HTTPStatus.NOT_FOUND),
    ))
def test_pages_avaiiability(parametrized_client, url, method, status):
    response = getattr(parametrized_client, method)(url)
    assert response.status_code == status

@pytest.mark.parametrize('url, redirect_url', (
    (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture('login_url')),
    (pytest.lazy_fixture('delete_url'), pytest.lazy_fixture('login_url')),
))
def test_redirect_for_anonymous(client, url, redirect_url):
    assertRedirects(client.get(url), f'{redirect_url}?next={url}')
