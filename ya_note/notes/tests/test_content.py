from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Название записки',
            text='Текст записки',
            author=cls.author,
            slug='note'
        )

    def test_note_in_author_object_list(self):
        response = self.auth_author.get(self.HOME_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_reader_object_list(self):
        response = self.auth_reader.get(self.HOME_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_create_and_edit_contain_form(self):
        urls = [
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None)
        ]
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.auth_author.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
