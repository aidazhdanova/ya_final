from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from ..models import Group, Post
from django.core.cache import cache
from django.urls import reverse
from http import HTTPStatus

User = get_user_model()


class PostsUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user_1')
        cls.user_2 = User.objects.create_user(username='user_2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_user = Client()
        self.author = Client()
        self.author.force_login(self.user)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user_2)
        cache.clear()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse(
                'posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): 'posts/create_post.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user}): 'posts/profile.html',
            reverse(
                'posts:post_create'): 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.author.get(adress)
                self.assertTemplateUsed(response, template)

    def test_authorized_user_urls_status_code(self):
        """Проверка status_code для авторизованного пользователя."""
        field_urls_code = {
            reverse(
                'posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:post_create'): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse(
                'posts:profile',
                kwargs={'username': self.user}): HTTPStatus.OK,
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse(
                'posts:follow_index'): HTTPStatus.OK,
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user}): HTTPStatus.FOUND,
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user}): HTTPStatus.FOUND,
        }
        for url, response_code in field_urls_code.items():
            with self.subTest(url=url):
                status_code = self.authorized_user.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_unauthorized_user_urls_status_code(self):
        """Проверка status_code для неавторизованного пользователя."""
        field_urls_code = {
            reverse(
                'posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:post_create'): HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse(
                'posts:profile',
                kwargs={'username': self.user}): HTTPStatus.OK,
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse(
                'posts:follow_index'): HTTPStatus.FOUND,
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user}): HTTPStatus.FOUND,
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user}): HTTPStatus.FOUND,
        }
        for url, response_code, in field_urls_code.items():
            with self.subTest(url=url):
                status_code = self.guest_user.get(url).status_code
                self.assertEqual(status_code, response_code)
