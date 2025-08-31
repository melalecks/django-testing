from http import HTTPStatus
from .base import BaseTest


class TestRoutes(BaseTest):

    def test_pages_availability(self):
        test_cases = [
            # Доступность страниц для неавторизованного пользователя
            ('home', self.client, 'get', HTTPStatus.OK),
            ('login', self.client, 'get', HTTPStatus.OK),
            ('signup', self.client, 'get', HTTPStatus.OK),
            ('logout', self.client, 'post', HTTPStatus.OK),

            # Доступность страниц для автора
            ('list', self.auth_author, 'get', HTTPStatus.OK),
            ('success', self.auth_author, 'get', HTTPStatus.OK),
            ('add', self.auth_author, 'get', HTTPStatus.OK),
            ('edit', self.auth_author, 'get', HTTPStatus.OK),
            ('delete', self.auth_author, 'get', HTTPStatus.OK),
            ('detail', self.auth_author, 'get', HTTPStatus.OK),

            # Доступность страниц для читателя
            ('edit', self.auth_reader, 'get', HTTPStatus.NOT_FOUND),
            ('delete', self.auth_reader, 'get', HTTPStatus.NOT_FOUND),
            ('detail', self.auth_reader, 'get', HTTPStatus.NOT_FOUND),
        ]

        for url_name, client, method, status in test_cases:
            with self.subTest(url_name=url_name, client=client, method=method):
                url = self.urls[url_name]
                response = getattr(client, method)(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = self.urls['login']

        urls_to_test = [
            'list',
            'success',
            'add',
            'edit',
            'delete',
            'detail'
        ]

        for url_name in urls_to_test:
            with self.subTest(url_name=url_name):
                url = self.urls[url_name]
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
