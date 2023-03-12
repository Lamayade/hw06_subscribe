from django.conf import settings
from django.test import TestCase

from posts.models import Comment, Follow, Group, Post
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


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Тестовая запись',
            author=cls.user,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Довольно длинный текст комментария',
            author=cls.user,
        )

    def test_posts_comment_verbose_names_are_correct(self):
        """Check if for comment fields verbose names created correctly"""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Запись',
            'text': 'Содержание комментария',
            'created': 'Дата комментария',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name, expected_value
                )

    def test_posts_comment_has_correct_object_name(self):
        """Check if str(comment) returns self_text correct"""
        comment = CommentModelTest.comment
        self.assertEqual(
            str(comment), comment.text[:settings.MAX_COMMENT_SELF_TEXT_LENGTH]
        )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def test_posts_follow_verbose_names_are_correct(self):
        """Check if for follow fields verbose names created correctly"""
        follow = FollowModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name, expected_value
                )

    def test_posts_follow_has_correct_object_name(self):
        """Check if str(follow) returns self_text correct"""
        follow = FollowModelTest.follow
        self.assertEqual(
            str(follow),
            ('Подписки '
             + follow.user.username)[:settings.MAX_FOLLOW_SELF_TEXT_LENGTH]
        )
