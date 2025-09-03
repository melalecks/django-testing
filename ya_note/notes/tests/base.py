from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTest(TestCase):

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

        cls.urls = {
            'home': reverse('notes:home'),
            'login': reverse('users:login'),
            'signup': reverse('users:signup'),
            'logout': reverse('users:logout'),
            'list': reverse('notes:list'),
            'success': reverse('notes:success'),
            'add': reverse('notes:add'),
            'edit': reverse('notes:edit', args=(cls.note.slug,)),
            'delete': reverse('notes:delete', args=(cls.note.slug,)),
            'detail': reverse('notes:detail', args=(cls.note.slug,)),
        }
