import shutil
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.models import Group, Post, Follow
from django.conf import settings
import tempfile
from django.core.cache import cache


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
             
    def setUp(self):
        self.authorized_client = Client()
        cache.clear()
        self.authorized_client.force_login(self.user)

    def check_context(self, context):
        with self.subTest(context=context):
            self.assertEqual(context.text, self.post.text)
            self.assertEqual(context.author, self.post.author)
            self.assertEqual(context.group.id, self.post.group.id)
            self.assertEqual(context.image, self.post.image)

    def test_forms_correct(self):
        """Проверка коректности формы."""
        context = {
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        }
        for reverse_page in context:
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                self.assertIsInstance(
                    response.context['form'].fields['text'],
                    forms.fields.CharField)
                self.assertIsInstance(
                    response.context['form'].fields['group'],
                    forms.fields.ChoiceField)
                self.assertIsInstance(
                    response.context['form'].fields['image'],
                    forms.fields.ImageField)

    def test_groups_list_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'], self.group)
        self.check_context(response.context['page_obj'][0])

    def test_index_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_context(response.context['page_obj'][0])

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}))
        self.check_context(response.context['post'])

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}))
        self.assertEqual(response.context['author'], self.user)
        self.check_context(response.context['page_obj'][0])

    def test_cache(self):
        """Проверка кэша"""
        post = Post.objects.create(
            text='Текст',
            author=self.user)
        content_add = self.authorized_client.get(
            reverse('posts:index')).content
        post.delete()
        content_delete = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(content_add, content_delete)
        cache.clear()
        content_cache_clear = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(content_add, content_cache_clear)

    def test_paginator_correct_context(self):
        """Шаблоны group_list, index, profile
        сформированы с корректным Paginator."""
        paginator_objects = []
        for i in range(1, 18):
            new_post = Post(
                author=PostsViewsTests.user,
                text='Тестовый пост ' + str(i),
                group=PostsViewsTests.group
            )
            paginator_objects.append(new_post)

        Post.objects.bulk_create(paginator_objects)
        paginator_data = {
            'index': reverse('posts:index'),
            'group': reverse(
                'posts:group_list',
                kwargs={'slug': PostsViewsTests.group.slug}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': PostsViewsTests.user.username}
            )
        }
        for paginator_place, paginator_page in paginator_data.items():
            with self.subTest(paginator_place=paginator_place):
                response_page_1 = self.authorized_client.get(paginator_page)
                response_page_2 = self.authorized_client.get(
                    paginator_page + '?page=2'
                )
                self.assertEqual(len(
                    response_page_1.context['page_obj']),
                    10
                )
                self.assertEqual(len(
                    response_page_2.context['page_obj']),
                    8
                )


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='author',
        )
        cls.follower = User.objects.create(
            username='follower',
        )
        cls.post = Post.objects.create(
            text='Подпишитесь',
            author=cls.author,
        )

    def setUp(self):
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(self.follower)
        self.follower_client = Client()
        self.follower_client.force_login(self.author)

    def test_follow_user(self):
        """Проверка возможности подписки на пользователя."""
        cnt_follow = Follow.objects.count()
        self.follower_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.follower}))
        follow = Follow.objects.all().latest('id')
        self.assertEqual(Follow.objects.count(), cnt_follow + 1)
        self.assertEqual(follow.user_id, self.author.id)
        self.assertEqual(follow.author_id, self.follower.id)
        

    def test_unfollow_user(self):
        """Проверка возможности отписки от пользователя."""
        Follow.objects.create(
            user=self.author,
            author=self.follower)
        cnt_follow = Follow.objects.count()
        self.follower_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.follower}))
        self.assertEqual(Follow.objects.count(), cnt_follow - 1)

    def test_follow_authors(self):
        """Проверка записей у тех кто подписан на автора."""
        post = Post.objects.create(
            author=self.author,
            text="Подпишитесь")
        Follow.objects.create(
            user=self.follower,
            author=self.author)
        response = self.author_client.get(
            reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'].object_list)

    def test_not_follow_authors(self):
        """Проверка записей у тех кто не подписан на автора."""
        post = Post.objects.create(
            author=self.author,
            text="Подпишитесь")
        response = self.author_client.get(
            reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'].object_list)
