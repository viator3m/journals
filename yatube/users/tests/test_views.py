from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UsersViewsTest(TestCase):
    """Проверка, что во view-функциях используются корректные шаблоны"""

    def setUp(self) -> None:
        self.guest_client = Client()

        self.user = User.objects.create_user(username='noname')
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)

    def test_check_namespace_auth(self):
        """Проверка, корректности шаблонов для авторизованного пользователя"""

        templates_name = {
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change/done'):
                'users/password_change_done.html',
            reverse('users:logout'):
                'users/logged_out.html'
        }

        for name, template in templates_name.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)

                self.assertTemplateUsed(response, template)

    def test_check_namespace_guest(self):
        """Проверка, корректности шаблонов для гостевого пользователя"""

        templates_name = {
            reverse('users:signup'):
                'users/signup.html',
            reverse('users:login'):
                'users/login.html',
            reverse('users:password_reset'):
                'users/password_reset_form.html',
            reverse('users:password_reset/done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_confirm',
                    args=('_',
                          default_token_generator.make_token(self.user))):
                'users/password_reset_confirm.html',
            reverse('password_reset_complete'):
                'users/password_reset_complete.html',
        }

        for name, template in templates_name.items():
            with self.subTest(name=name):
                response = self.guest_client.get(name)

                self.assertTemplateUsed(response, template)

    def test_signup_show_correct_context_form(self):
        """Проверка, корректности формы регистрации"""

        response = self.authorized_client.get(reverse('users:signup'))
        context = response.context.get('form')
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                field = context.fields.get(value)

                self.assertIsInstance(field, expected)
