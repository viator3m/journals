from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    """Тестирование моделей приложения Post."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='Тестовый слаг',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост' * 3,
        )

    def test_models_have_correct_objects_name(self):
        """Проверка работы метода __str__ в моделях Post и Group."""

        post = PostModelTest.post
        self.assertEqual(str(post), post.text[:15])
        group = PostModelTest.group
        self.assertEqual(str(group), group.title)

    def test_verbose_name_post(self):
        """Проверка verbose_name модели Post."""

        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Сообщество',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_verbose_name_group(self):
        """Проверка verbose_name модели Group."""

        group = PostModelTest.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Адрес',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text_post(self):
        """Проверка help_text модели Post."""

        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )

    def test_help_text_group(self):
        """Проверка help_text модели Group."""

        group = PostModelTest.group
        field_help_text = {
            'title': 'Введите название сообщества',
            'slug': ('Укажите адрес для страницы задачи. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания'),
            'description': 'Введите описание сообщества',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value
                )
