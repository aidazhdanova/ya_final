from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    """Создаем тестовый пост и группу."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Проверка вывода вводного текста до 15 символов."""
        post = PostModelTest.post
        self.assertEqual(str(post), post.text[:15])

    def test_models_name_title_field_group(self):
        """Проверка наличия поля title в модели данных группы."""
        group = PostModelTest.group
        self.assertEquals(group.title, str(group))
