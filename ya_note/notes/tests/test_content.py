from .base import BaseTest
from notes.forms import NoteForm


class TestContent(BaseTest):

    def test_note_in_author_object_list(self):
        response = self.auth_author.get(self.urls['list'])
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

    def test_note_not_in_reader_object_list(self):
        response = self.auth_reader.get(self.urls['list'])
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_create_and_edit_contain_form(self):
        urls = [self.urls['edit'], self.urls['add']]
        for url_name in urls:
            with self.subTest(url_name=url_name):
                response = self.auth_author.get(url_name)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
