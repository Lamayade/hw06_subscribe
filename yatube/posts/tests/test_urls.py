from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from users.forms import User


class PostPagesURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.non_author = User.objects.create_user(username='Not an author')
        cls.test_group = Group.objects.create(
            title='Заголовок тестовой группы',
            slug='test-slug',
            description='Описание тестовой группы',
        )
        cls.test_post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.test_group,
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.non_author_client = Client()
        self.non_author_client.force_login(self.non_author)

    def test_posts_urls_exist_at_desired_location(self):
        """Check the existence of '/.../' pages.

        Check if the HTTP status code is 'OK' for '/.../' pages
        """
        urls = (
            '/',
            f'/group/{self.test_group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.test_post.id}/',
        )
        for url in urls:
            with self.subTest(field=url):
                self.assertEqual(
                    self.client.get(url).status_code, HTTPStatus.OK
                )

    def test_posts_edit_page_is_available_for_author(self):
        """Check if the edit page is available for the creator"""
        url = f'/posts/{self.test_post.id}/edit/'
        response = self.authorized_client.get(url)
        self.assertEqual(
            response.status_code, HTTPStatus.OK
        )

    def test_posts_private_urls_redirect_guest(self):
        """Check for the guest redirection if URL is private.

        Check if the HTTP status code is 'FOUND' for private pages
        """
        urls = (
            '/create/',
            f'/posts/{self.test_post.id}/edit/',
        )
        for url in urls:
            with self.subTest(field=url):
                self.assertEqual(
                    self.client.get(url).status_code, HTTPStatus.FOUND
                )

    def test_posts_edit_page_redirects_guest_to_login_page(self):
        """ Check the guest redirection from edit to login page.

        Check the case when a guest client trying to change post.
        He should be redirected to the login page, then (if he created post)
        to the edit post page.
        """
        url = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.test_post.id}
        )
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse(
                'users:login'
            ) + '?next=' + reverse(
                'posts:post_edit',
                kwargs={'post_id': self.test_post.id}
            )
        )

    def test_posts_edit_page_redirects_non_author_to_post_page(self):
        """ Check the non-author redirection from edit to post detail page.

        Check the case when the non-author trying to change post.
        He should be redirected to the post detail page.
        """
        self.non_author_client.force_login(self.non_author)
        url = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.test_post.id}
        )
        response = self.non_author_client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.test_post.id}
            )
        )

    def test_posts_create_page_is_available_for_authorized(self):
        """Check if the authorized user can create post"""
        url = '/create/'
        self.assertEqual(
            self.authorized_client.get(url).status_code, HTTPStatus.OK
        )

    def test_posts_create_page_redirects_guest_to_login_page(self):
        """Check the guest redirection from post creation page to login page"""
        url = reverse(
            'posts:post_create'
        )
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse(
                'users:login',
            ) + '?next=' + reverse(
                'posts:post_create'
            )
        )

    def test_posts_wrong_url_does_not_exist(self):
        """Check the non-existence of the wrong '/.../' page.

        Check if the HTTP status code is 'NOT FOUND'
        for the '/unexisting_page/' page
        """
        url = '/unexisting_page/'
        self.assertEqual(
            self.client.get(url).status_code, HTTPStatus.NOT_FOUND
        )

    def test_posts_urls_use_correct_template(self):
        """Check templates for '/.../' pages"""
        field_responses = {
            '/': 'posts/index.html',
            f'/group/{self.test_group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.test_post.id}/': 'posts/post_detail.html',
            f'/posts/{self.test_post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for field, expected_value in field_responses.items():
            with self.subTest(field=field):
                self.assertTemplateUsed(
                    self.authorized_client.get(field), expected_value
                )
