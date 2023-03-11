from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from users.forms import User


class CachedPagesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.test_group = Group.objects.create(
            title='Заголовок тестовой группы',
            description='Описание тестовой группы',
            slug='test-slug',
        )
        cls.test_post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.test_group,
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_cached_post_is_on_the_index_page(self):
        """Check if the cached post is remaining on the index page.

        Check if the new post after delete is remaining on the index page,
        but it's disappearing after clearing cache """
        new_test_post = Post.objects.create(
            text='Новый пост',
            author=self.user,
            group=self.test_group,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.first().delete()
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.id, new_test_post.id)
        self.assertEqual(first_object.text, new_test_post.text)
        self.assertEqual(first_object.group, new_test_post.group)
        self.assertEqual(first_object.author, new_test_post.author)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.id, self.test_post.id)
        self.assertEqual(first_object.text, self.test_post.text)
        self.assertEqual(first_object.group, self.test_post.group)
        self.assertEqual(first_object.author, self.test_post.author)
