from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, Comment

User = get_user_model()


class PostsFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_client_create_post(self):
        """Проверка создания записи для неавторизированного пользователя."""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('login') + '?next=' + reverse('posts:post_create')
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_post_form(self):
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': self.post.text,
        }
        response = self.authorized_client.post(reverse(
            'posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user,
                group=self.group,
            ).exists()
        )

    def test_edit_post_form(self):
        form_data = {
            'group': self.group.id,
            'text': self.post.text,
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user,
                group=self.group,
            ).exists()
        )

    def test_authorized_user_create_comment(self):
        """Проверка создания коммента авторизированным пользователем."""
        comments_count = Comment.objects.count()
        form_data = {'text': 'Тестовый коментарий'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[
                    self.post.id]),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.latest('id')
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post_id, self.post.id)
        self.assertEqual(comment.author, self.user)
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[self.post.id]))

    def test_guest_client_create_comment(self):
        """Проверка создания коммента неавторизированным пользователем."""
        cmnt_count = Comment.objects.count()
        post = Post.objects.create(
            author=self.user,
            text='Текст')
        form_data = {'text': 'Тестовый комментарий'}
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post.id}),
            follow=True,
            data=form_data)
        redirect = reverse('login') + '?next=' + reverse(
            'posts:add_comment', kwargs={'post_id': post.id})
        self.assertEqual(Comment.objects.count(), cmnt_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, redirect)
