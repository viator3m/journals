from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class SignUpFormTest(TestCase):
    """Проверяет форму регистрации нового пользователя."""

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_signup_new_user(self):
        """Проверяет, что при оправке формы регистрации создается новый
        пользователь и перенаправляется на стартовую страницу"""

        form_data = {
            'username': 'redbadhead',
            'password1': 'backslashescape',
            'password2': 'backslashescape'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:index'))
        self.assertTrue(
            User.objects.filter(
                username='redbadhead'
            ).exists()
        )
