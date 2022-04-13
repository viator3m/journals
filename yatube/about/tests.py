from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutTests(TestCase):
    """Проверка доступности страниц и корректного использования шаблонов"""

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_correct_url(self):
        """Проверка использования правильных шаблонов"""

        templates_name = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }

        for name, templates in templates_name.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))

                self.assertTemplateUsed(response, templates)

    def test_correct_urls(self):
        """Проверка доступности страниц about и tech любому пользователю"""

        names = (
            'about:author',
            'about:tech'
        )

        for name in names:
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))

                self.assertEqual(response.status_code, HTTPStatus.OK)
