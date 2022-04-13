from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UserAuthURLTest(TestCase):
    """Проверка доступности страниц и
    корректности использования шаблонов в приложении users
    для авторизованного пользователя."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='noname')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_availability_for_auth_user(self):
        """Проверка доступности страниц:
                                        – '/auth/logout/',
                                        – '/auth/password_change/',
                                        – '/auth/password_change/done/'
        для авторизованного пользователя"""

        pages_name = (
            reverse('users:logout'),
            reverse('users:password_change'),
            reverse('users:password_change/done'),
        )

        for address in pages_name:
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)

                self.assertEqual(response.status_code, HTTPStatus.OK)


class UserGuestURLTest(TestCase):
    """Проверка доступности страниц и
    корректности использования шаблонов в приложении users
    для анонимного пользователя."""

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='noname')

    def test_page_availability_for_guest_user(self):

        pages_name = (
            reverse('users:signup'),
            reverse('users:login'),
            reverse('users:password_reset'),
            reverse('users:password_reset/done'),
            reverse('users:password_reset_complete'),
            reverse('users:password_reset_confirm',
                    args=('_',
                          default_token_generator.make_token(self.user))),
        )

        for address in pages_name:
            with self.subTest(address=address):
                response = self.guest_client.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)
