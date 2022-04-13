from django.test import TestCase, Client


class TemplateTest(TestCase):

    def setUp(self) -> None:
        self.client = Client()

    def test_unexist_page_render_custom_template(self):
        """Проверяет, что несуществующая страница отдает кастомный шаблон"""

        url = '/unexisting_page/'
        template = 'core/404.html'

        response = self.client.get(url)

        self.assertTemplateUsed(response, template)

