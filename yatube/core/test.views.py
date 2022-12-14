from http import HTTPStatus
from django.test import Client, TestCase


class ViewTestClass(TestCase):
    """Cтраница 404 отдаёт кастомный шаблон."""
    def setUp(self):
        self.client = Client()

    def test_page_error(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
