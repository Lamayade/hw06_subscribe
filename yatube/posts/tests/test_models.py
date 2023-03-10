from django.conf import settings
from django.test import TestCase

from posts.models import Group, Post
from users.forms import User


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Довольно длинный заголовок тестовой группы',
            slug='test-slug',
            description='Описание тестовой группы',
        )

    def test_posts_group_verbose_names_are_correct(self):
        """Check if for group fields verbose names created as they should be"""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Уникальная часть URL группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_posts_group_has_correct_object_name(self):
        """Check if str(group) returns self_text correct"""
        group = GroupModelTest.group
        self.assertEqual(
            str(group), group.title[:settings.MAX_GROUP_SELF_TEXT_LENGTH])


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Заголовок тестовой группы',
            slug='test-slug',
            description='Описание тестовой группы',
        )

        cls.post = Post.objects.create(
            text='Довольно длинная тестовая запись',
            author=cls.user,
            group=cls.group,
        )

    def test_posts_verbose_names_are_correct(self):
        """Check if for post fields verbose names created as they should be"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Содержание записи',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_posts_post_has_correct_object_name(self):
        """Check if str(post) returns self_text correct"""
        post = PostModelTest.post
        self.assertEqual(
            str(post), post.text[:settings.MAX_POST_SELF_TEXT_LENGTH]
        )
