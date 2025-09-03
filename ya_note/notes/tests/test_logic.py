from http import HTTPStatus

from django.contrib.auth import get_user
from pytils.translit import slugify

from .base import BaseTest
from notes.forms import WARNING
from notes.models import Note


class TestLogic(BaseTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {'title': 'Другая записка',
                         'text': 'Другой текст записки',
                         'slug': 'slug'}

    def test_anonymous_cant_create_note(self):
        notes_count = Note.objects.count()
        self.client.post(self.urls['add'], data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_authorised_can_create_note(self):
        Note.objects.all().delete()
        self.auth_author.post(self.urls['add'], data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.author, get_user(self.auth_author))
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])

    def test_unable_to_create_identical_slug(self):
        self.auth_author.post(self.urls['add'], data=self.form_data)
        response = self.auth_author.post(self.urls['add'],
                                         data=self.form_data)
        form = response.context['form']
        self.assertFormError(form, 'slug', self.form_data['slug'] + WARNING)

    def test_slug_generation(self):
        Note.objects.all().delete()
        self.form_data['slug'] = ''
        self.auth_author.post(self.urls['add'], data=self.form_data)
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))

    def test_author_can_delete(self):
        count_before_delete = Note.objects.count()
        response = self.auth_author.delete(self.urls['delete'])
        self.assertEqual(Note.objects.count(), count_before_delete - 1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.urls['success'])

    def test_author_can_edit(self):
        response = self.auth_author.post(self.urls['edit'],
                                         data=self.form_data)
        self.assertRedirects(response, self.urls['success'])
        edit_note = Note.objects.get(id=self.note.id)
        self.assertEqual(edit_note.title, self.form_data['title'])
        self.assertEqual(edit_note.text, self.form_data['text'])
        self.assertEqual(edit_note.slug, self.form_data['slug'])
        self.assertEqual(edit_note.author, self.note.author)

    def test_reader_cant_delete(self):
        count_before_delete = Note.objects.count()
        response = self.auth_reader.delete(self.urls['delete'])
        self.assertEqual(Note.objects.count(), count_before_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())

    def test_reader_cant_edit(self):
        response = self.auth_reader.post(self.urls['edit'],
                                         data=self.form_data)
        edit_note = Note.objects.get(id=self.note.id)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(edit_note.title, self.note.title)
        self.assertEqual(edit_note.text, self.note.text)
        self.assertEqual(edit_note.slug, self.note.slug)
        self.assertEqual(edit_note.author, self.note.author)
