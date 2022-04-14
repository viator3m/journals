import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Post, Group, Follow
from ..views import NUMBER_OF_POSTS

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsBaseTest(TestCase):
    """Базовый класс для создания фикстур """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

        cls.user = User.objects.create_user(username='auth')

        cls.author = Client()
        cls.author.force_login(cls.user)

        cls.user_noname = User.objects.create_user(username='noname')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(user=cls.user_noname)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


class PostContextTest(PostViewsBaseTest):
    """Класс проверки контекста."""

    def setUp(self) -> None:
        self.post_id = self.post.pk

    def test_edit_and_create_pages_show_correct_context(self):
        """Проверяет корректность переданного контекста на странице
         редактирования поста."""

        urls = [
            reverse('posts:post_edit', args=[self.post_id]),
            reverse('posts:post_create'),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.author.get(url)
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                    'image': forms.fields.ImageField,
                }
                context = response.context.get('form')

                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = context.fields.get(value)

                        self.assertIsInstance(form_field, expected)

    def test_post_detail_show_correct_context(self):
        """Проверяет корректность переданного контекста на странице поста."""

        url = reverse('posts:post_detail', args=[self.post_id])

        response = self.authorized_client.get(url)
        post = response.context.get('post')

        self.assertEqual(post.text, 'Тестовый пост')
        self.assertEqual(str(post.author), 'auth', )
        self.assertEqual(str(post.group), 'Тестовая группа'),
        self.assertEqual(
            str(post.image), 'posts/' + self.uploaded.name
        )

    def test_index_group_profile_pages_show_correct_context(self):
        """Проверяет корректность переданного контекста на страницах:
        – index,
        – group/<slug>/
        – profile/<username>/

        Также проверяет, что созданный в фикстурах пост появился на
        вышеперечисленных страницах.
        """

        urls = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'})
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                context = response.context['page_obj']
                obj = context[0]

                self.assertEqual(obj.text, 'Тестовый пост')
                self.assertEqual(str(obj.author), 'auth', )
                self.assertEqual(str(obj.group), 'Тестовая группа'),
                self.assertEqual(
                    str(obj.image), 'posts/' + self.uploaded.name
                )


class PaginatorViewTest(PostViewsBaseTest):
    """Класс для проверки паджинатора"""

    def setUp(self) -> None:
        self.client = Client()
        [Post.objects.create(
            author=self.user,
            text=f'Тестовый пост_{i}',
            group=self.group,
        ) for i in range(15)]

    def test_first_page_contains_ten_records(self):
        """Проверяет, что на первой странице index будет 10 постов"""

        response = self.client.get(reverse('posts:index'))
        expected_numbers = NUMBER_OF_POSTS

        numbers_of_post = len(response.context['page_obj'])

        self.assertEqual(numbers_of_post, expected_numbers)

    def test_second_page_contains_six_records(self):
        """Проверяет, что на второй странице index будет 6 постов"""

        response = self.client.get(reverse('posts:index') + '?page=2')
        expected_numbers = 6

        numbers_of_post = len(response.context['page_obj'])

        self.assertEqual(numbers_of_post, expected_numbers)


class PostTemplatesTest(PostViewsBaseTest):
    """Класс для проверки корректности используемых шаблонов"""

    def test_pages_uses_correct_templates(self):
        """View-функции используют корректные шаблоны"""

        username = self.user
        post_id = self.post.pk
        templates_name = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': f'{username}'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': f'{post_id}'}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': f'{post_id}'}):
                'posts/create_post.html'
        }

        for name, template in templates_name.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(name)
                if name == f'/posts/{post_id}/edit/':
                    response = self.author.get(name)

                self.assertTemplateUsed(response, template)


class PostCreatingTest(PostViewsBaseTest):
    """Класс проверяет, что если указать группу при создании поста,
    то пост не появится в другой группе"""

    def setUp(self) -> None:
        self.group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2'
        )

    def test_creating_post_is_not_other_group(self):
        """Проверка, что пост не появился в другой группе"""

        url = reverse('posts:group_list', args=[self.group.slug])

        response = self.authorized_client.get(url)
        context = response.context['page_obj']

        self.assertNotIn(self.post, context)


class CacheTest(TestCase):
    """Проверка кэширования"""

    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username='user_noname')
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user
        )

    def test_cache_index(self):
        """Проверка кэширования главной страницы"""

        url = reverse('posts:index')

        response = self.client.get(url).content
        Post.objects.all().delete()
        response_upd = self.client.get(url).content

        self.assertEqual(response, response_upd)

        cache.clear()
        response_upd_again = self.client.get(url).content

        self.assertNotEqual(response, response_upd_again)


class SubscribeTest(PostViewsBaseTest):
    """Тестирование системы подписки"""

    def setUp(self) -> None:
        self.post = Post.objects.create(
            text='test_post_subscribe',
            author=self.user
        )

    def test_auth_subscribe(self):
        """Авторизованный пользователь может подписаться на автора,
        и остается на странице постов автора."""

        url = reverse('posts:profile_follow', args=(self.user,))
        url_redirect = reverse('posts:profile', args=(self.user,))
        response = self.authorized_client.get(url, follow=True)
        follow_success = Follow.objects.filter(
            user=self.user_noname,
            author=self.user
        ).exists()

        self.assertRedirects(response, url_redirect)
        self.assertTrue(follow_success)

    def test_auth_unsubscribe(self):
        """Авторизованный пользователь может отписаться от автора,
        и остается на странице постов автора."""

        url = reverse('posts:profile_unfollow', args=(self.user,))
        url_redirect = reverse('posts:profile', args=(self.user,))
        response = self.authorized_client.get(url, follow=True)
        follow_success = Follow.objects.filter(
            user=self.user_noname,
            author=self.user
        ).exists()

        self.assertRedirects(response, url_redirect)
        self.assertFalse(follow_success)

    def test_new_post_if_subscribe(self):
        """Проверяет, что новый пост появляется в ленте подписчиков."""

        Follow.objects.create(user=self.user_noname, author=self.user)
        url = reverse('posts:follow_index')

        response = self.authorized_client.get(url)

        self.assertContains(response, self.post)

    def test_new_post_if_not_subscribe(self):
        """Проверяет, что новый пост НЕ появляется в ленте у тех,
        кто не подписан на автора."""

        url = reverse('posts:follow_index')

        response = self.authorized_client.get(url)

        self.assertNotContains(response, self.post)
