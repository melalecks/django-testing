from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestLogic(TestCase):
    ADD_NOTE_URL = reverse('notes:add')
    REDIRECT_URL = reverse('notes:success')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Записка',
            text='Текст записки',
            author=cls.author,
            slug='note'
        )
        cls.form_data = {'title': 'Другая записка',
                         'text': 'Другой текст записки',
                         'slug': 'slug'}

    def test_anonymous_cant_create_note(self):
        notes_count = Note.objects.count()
        self.client.post(self.ADD_NOTE_URL, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_authorised_can_create_note(self):
        notes_count = Note.objects.count()
        self.auth_author.post(self.ADD_NOTE_URL, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count + 1)

    def test_unable_to_create_identical_slug(self):
        self.auth_author.post(self.ADD_NOTE_URL, data=self.form_data)
        response = self.auth_author.post(self.ADD_NOTE_URL,
                                         data=self.form_data)
        form = response.context['form']
        self.assertFormError(form, 'slug', self.form_data['slug'] + WARNING)

    def test_slug_generation(self):
        self.form_data['slug'] = ''
        self.auth_author.post(self.ADD_NOTE_URL, data=self.form_data)
        new_note = Note.objects.latest('id')
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))

    def test_author_can_delete(self):
        count_before_delete = Note.objects.count()
        response = self.auth_author.delete(reverse(
            'notes:delete', args=(self.note.slug,)
        ))
        self.assertEqual(Note.objects.count(), count_before_delete - 1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.REDIRECT_URL)

    def test_author_can_edit(self):
        response = self.auth_author.post(
            reverse('notes:edit', args=(self.note.slug,)),
            data=self.form_data
        )
        self.assertRedirects(response, self.REDIRECT_URL)
        self.note.refresh_from_db()
        self.assertEqual(
            (self.note.title, self.note.text, self.note.slug),
            (self.form_data['title'], self.form_data['text'],
             self.form_data['slug'])
        )

    def test_reader_cant_delete(self):
        count_before_delete = Note.objects.count()
        response = self.auth_reader.delete(reverse(
            'notes:delete', args=(self.note.slug,)
        ))
        self.assertEqual(Note.objects.count(), count_before_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())

    def test_reader_cant_edit(self):
        response = self.auth_reader.post(
            reverse('notes:edit', args=(self.note.slug,)),
            data=self.form_data
        )
        self.note.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertNotEqual(
            (self.note.title, self.note.text, self.note.slug),
            (self.form_data['title'], self.form_data['text'],
             self.form_data['slug'])
        )
