from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from ..models import Group, Post

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
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user_2)

    def test_url_uses_correct_index(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_url_uses_correct_group(self):
        response = self.guest_client.get(f'/group/{self.group.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_url_uses_correct_profile(self):
        response = self.guest_client.get(f'/profile/{self.user}/')
        self.assertEqual(response.status_code, 200)

    def test_url_authorized_post_id(self):
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_create_url_authorized(self):
        """Проверка возможности для авторизованного пользователя
         создать пост."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_edit_url_unauthorized(self):
        """Проверка возможности для неавторизованного пользователя
         редактировать пост."""
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_create_url_unauthorized(self):
        """Проверка возможности для неавторизованного пользователя
         создать пост."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_edit_url_not_by_author(self):
        """Проверка возможности для не автора редактировать пост."""
        response = self.authorized_client_2.get(
            f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_unexisting_url(self):
        """Проверка несуществующей страницы."""
        response = self.guest_client.get('/unexisting/')
        self.assertEqual(response.status_code, 404)

    def test_home_url_uses_correct_template_index(self):
        """Проверяем общедоступные страницы."""
        response = self.authorized_client.get('/')
        self.assertTemplateUsed(response, 'posts/index.html')

    def test_home_url_uses_correct_template_group_list(self):
        """Проверяем общедоступные страницы."""
        response = self.authorized_client.get(f'/group/{self.group.slug}/')
        self.assertTemplateUsed(response, 'posts/group_list.html')

    def test_home_url_uses_correct_template_profile(self):
        """Проверяем общедоступные страницы."""
        response = self.authorized_client.get(f'/profile/{self.user}/')
        self.assertTemplateUsed(response, 'posts/profile.html')

    def test_home_url_uses_correct_template_post_detail(self):
        """Проверяем общедоступные страницы."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/')
        self.assertTemplateUsed(response, 'posts/post_detail.html')

    def test_home_url_uses_correct_template_profile_edit(self):
        """Проверяем общедоступные страницы."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_home_url_uses_correct_template_create(self):
        """Проверяем общедоступные страницы."""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')
