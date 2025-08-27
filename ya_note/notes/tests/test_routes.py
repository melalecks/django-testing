from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.reader = User.objects.create(username='Гость')
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Название записки',
            text='Текст записки',
            author=cls.author,
            slug='note'
        )

    def test_pages_availability(self):
        test_cases = [
            # Доступность страниц для неавторизованного пользователя
            ('notes:home', Client(), 'get', HTTPStatus.OK, None),
            ('users:login', Client(), 'get', HTTPStatus.OK, None),
            ('users:signup', Client(), 'get', HTTPStatus.OK, None),
            ('users:logout', Client(), 'post', HTTPStatus.OK, None),

            # Доступность страниц для автора
            ('notes:list', self.auth_author, 'get', HTTPStatus.OK, None),
            ('notes:success', self.auth_author, 'get', HTTPStatus.OK, None),
            ('notes:add', self.auth_author, 'get', HTTPStatus.OK, None),
            ('notes:edit', self.auth_author, 'get', HTTPStatus.OK,
             (self.note.slug,)),
            ('notes:delete', self.auth_author, 'get', HTTPStatus.OK,
             (self.note.slug,)),
            ('notes:detail', self.auth_author, 'get', HTTPStatus.OK,
             (self.note.slug,)),

            # Доступность страниц для читателя
            ('notes:edit', self.auth_reader, 'get', HTTPStatus.NOT_FOUND,
             (self.note.slug,)),
            ('notes:delete', self.auth_reader, 'get', HTTPStatus.NOT_FOUND,
             (self.note.slug,))
        ]

        for name, client, method, status, args in test_cases:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = getattr(client, method)(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
