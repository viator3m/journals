from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostUrlBaseTest(TestCase):
    """Базовый класс для создания фикстур"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.author = Client()
        cls.author.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='noname')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


class PostURLsGuestTests(PostUrlBaseTest):
    """Проверка доступности страниц и шаблонов в приложении posts
    для гостевого пользователя."""

    def test_public_page_available_guest(self):
        """
        Проверяет, что страницы:
                                — стартовая,
                                — страница сообщества,
                                — страница профиля,
                                — страница с детализацией поста
        доступны любому пользователю
        """

        pages_list = (
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user]),
            reverse('posts:post_detail', args=[self.post.id])
        )

        for url in pages_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)

                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Проверьте доступность страницы {url}'
                )

    def test_unexisting_page_return_404(self):
        """Проверяет, что несуществующая страница возвращает 404."""

        url = '/unexist/'

        response = self.guest_client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_guest_create_post(self):
        """Проверяет, что неавторизованный пользователь будет перенаправлен
           на страницу авторизации при попытке создать пост."""

        url = reverse('posts:post_create')
        login = reverse('users:login')
        create = reverse('posts:post_create')
        expected_redirect = f"{login}?next={create}"

        response = self.guest_client.get(url)

        self.assertRedirects(response, expected_redirect)

    def test_guest_edit_post(self):
        """Проверяет, что неавторизованный пользователь будет перенаправлен
           на страницу авторизации при попытке редактировать пост."""

        url = reverse('posts:post_edit', args=['1'])
        login = reverse('users:login')
        expected_redirect = f'{login}?next={url}'

        response = self.guest_client.get(url)

        self.assertRedirects(response, expected_redirect)


class PostURLsAuthTest(PostUrlBaseTest):
    """Проверка доступности страниц и шаблонов в приложении posts
    для авторизованного пользователя."""

    def test_auth_create_post(self):
        """Проверяет, что страница создания поста доступна
         авторизованному пользователю."""

        url = reverse('posts:post_create')

        response = self.authorized_client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_non_author_edit_post(self):
        """Проверяет, что авторизованный пользователь будет перенаправлен
         на страницу с постом, если он не автор поста."""

        url = reverse('posts:post_edit', args=[self.post.id])
        expected_redirect = reverse('posts:post_detail', args=[self.post.id])

        response = self.authorized_client.get(url, follow=True)

        self.assertRedirects(response, expected_redirect)

    def test_author_edit_post(self):
        """Проверяет, что автору поста доступна страница
         с редактированием поста."""

        url = reverse('posts:post_edit', args=[self.post.id])

        response = self.author.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_templates(self):
        """Проверяет, что запросы на адреса используют правильные шаблоны."""

        templates_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list', args=['test-slug']):
                'posts/group_list.html',
            reverse('posts:profile', args=['auth']):
                'posts/profile.html',
            reverse('posts:post_detail', args=[self.post.id]):
                'posts/post_detail.html',
            reverse('posts:post_edit', args=[self.post.id]):
                'posts/create_post.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
        }

        for url, template in templates_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if url == reverse('posts:post_edit', args=[self.post.id]):
                    response = self.author.get(url)
                self.assertTemplateUsed(response, template)
