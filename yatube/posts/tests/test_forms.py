import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class FormTest(TestCase):
    """Базовый класс для создания фикстур."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

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

        cls.post = Post.objects.create(
            text='test_post',
            author=cls.user_noname
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(FormTest):
    """Тестирование форм создания и редактирования поста """

    def test_form_create_new_post(self):
        """Проверяет, что при отправке формы создания поста создается новый пост
        и пользователя перенаправляет на страницу со всеми его постами """

        text = 'new_post'

        form_data = {
            'text': text,
            'author': self.user_noname,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(text=text)

        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': f'{self.user_noname}'})
        )
        self.assertEqual(post.text, text)
        self.assertEqual(str(post.image), 'posts/' + str(self.uploaded))

    def test_form_edit_post(self):
        """Проверяет, что при отправке формы редактирования поста сохраняются
        изменения и пользователя перенаправляет на страницу поста """

        post = Post.objects.create(text='old_post', author=self.user_noname)
        text = 'edited_post'
        form_data = {'text': text}

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{post.pk}'}),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{post.pk}'}))
        self.assertTrue(
            Post.objects.filter(
                text='edited_post'
            ).exists()
        )


class CommentTest(FormTest):
    """Класс для проверки комментариев."""

    def setUp(self) -> None:
        self.form_data = {'text': 'Тестовый комментарий'}

    def try_create_comment(self, client):
        url_comment = reverse('posts:add_comment', args=(self.post.pk,))
        url_post_detail = reverse('posts:post_detail', args=(self.post.pk,))
        client.post(
            url_comment,
            data=self.form_data,
            follow=True)
        response = client.get(url_post_detail)
        return response

    def test_auth_create_comment(self):
        """Комментировать может только авторизованный пользователь.
        Комментарий появляется на странице постаю."""

        response = self.try_create_comment(self.authorized_client)
        self.assertContains(response, self.form_data['text'])

    def test_guest_create_comment(self):
        """Гость не может комментировать посты"""

        response = self.try_create_comment(self.guest_client)
        self.assertNotContains(response, self.form_data['text'])
