import math
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post
from users.forms import User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.non_author = User.objects.create_user(username='Not an author')
        cls.test_group = Group.objects.create(
            title='Заголовок тестовой группы',
            description='Описание тестовой группы',
            slug='test-slug',
        )
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
        cls.test_post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.test_group,
            image=cls.uploaded
        )
        cls.test_another_group = Group.objects.create(
            title='Заголовок второй группы',
            description='Описание второй группы',
            slug='test-another-slug',
        )
        cls.test_another_post = Post.objects.create(
            text='Текст второго поста',
            author=cls.user,
            group=cls.test_another_group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_pages_use_correct_templates(self):
        """Check templates for '/.../' pages.

        Check if the 'posts/... .html' template is bonded with the
        post: ... name
        """
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'group_name': self.test_group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.test_post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.test_post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_index_page_shows_correct_context(self):
        """Check the context of the index page"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.id, self.test_another_post.id)
        self.assertEqual(first_object.text, self.test_another_post.text)
        self.assertEqual(first_object.group, self.test_another_post.group)
        self.assertEqual(first_object.author, self.test_another_post.author)
        self.assertEqual(first_object.image, self.test_another_post.image)

    def test_posts_group_list_page_shows_correct_context(self):
        """Check the context of the group list page"""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'group_name': self.test_group.slug})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.id, self.test_post.id)
        self.assertEqual(first_object.text, self.test_post.text)
        self.assertEqual(first_object.group, self.test_post.group)
        self.assertEqual(first_object.author, self.test_post.author)
        self.assertEqual(first_object.image, self.test_post.image)

    def test_posts_profile_page_shows_correct_context(self):
        """Check the context of the profile page"""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.id, self.test_another_post.id)
        self.assertEqual(first_object.text, self.test_another_post.text)
        self.assertEqual(first_object.group, self.test_another_post.group)
        self.assertEqual(first_object.author, self.test_another_post.author)
        self.assertEqual(first_object.image, self.test_another_post.image)

    def test_posts_post_detail_page_shows_correct_context(self):
        """Check the context of the post details page"""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.test_post.id})
        )
        post_object = response.context['chosen_post']
        self.assertEqual(post_object.id, self.test_post.id)
        self.assertEqual(post_object.text, self.test_post.text)
        self.assertEqual(post_object.group, self.test_post.group)
        self.assertEqual(post_object.author, self.test_post.author)
        self.assertEqual(post_object.image, self.test_post.image)

    def test_posts_create_post_page_shows_correct_context(self):
        """Check the context of the post create page"""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_edit_post_page_shows_correct_context(self):
        """Check the context of the post edit page"""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.test_post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_new_post_is_on_the_index_page(self):
        """Check if the new post is on the index page"""
        new_test_post = Post.objects.create(
            text='Новый пост',
            author=self.user,
            group=self.test_group,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.id, new_test_post.id)
        self.assertEqual(first_object.text, new_test_post.text)
        self.assertEqual(first_object.group, new_test_post.group)
        self.assertEqual(first_object.author, new_test_post.author)
        self.assertEqual(first_object.image, new_test_post.image)

    def test_posts_new_post_is_on_the_group_page(self):
        """Check if the new post is on the group page"""
        new_test_post = Post.objects.create(
            text='Новый пост',
            author=self.user,
            group=self.test_group,
            image=self.uploaded
        )
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'group_name': self.test_group.slug})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.id, new_test_post.id)
        self.assertEqual(first_object.text, new_test_post.text)
        self.assertEqual(first_object.group, new_test_post.group)
        self.assertEqual(first_object.author, new_test_post.author)
        self.assertEqual(first_object.image, new_test_post.image)

    def test_posts_new_post_is_on_the_profile_page(self):
        """Check if the new post is on the profile page"""
        new_test_post = Post.objects.create(
            text='Новый пост',
            author=self.user,
            group=self.test_group,
            image=self.uploaded
        )
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.id, new_test_post.id)
        self.assertEqual(first_object.text, new_test_post.text)
        self.assertEqual(first_object.group, new_test_post.group)
        self.assertEqual(first_object.author, new_test_post.author)
        self.assertEqual(first_object.image, new_test_post.image)

    def test_posts_new_post_is_not_on_the_another_group_page(self):
        """Check if the new post is not on the another group page"""
        new_test_post = Post.objects.create(
            text='Новый пост',
            author=self.non_author,
            group=self.test_group,
            image=self.uploaded,
        )
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'group_name': self.test_another_group.slug})
        )
        self.assertNotIn(new_test_post, response.context['page_obj'])


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.non_author = User.objects.create_user(username='Not an author')
        cls.test_group = Group.objects.create(
            title='Заголовок тестовой группы',
            description='Описание тестовой группы',
            slug='test-slug',
        )
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
        objs = ()
        for i in range(1, 2 * settings.NUMBER_OF_LAST_RECORDS + 1):
            objs += (Post(
                text=f'Пост №{i}',
                author=cls.user,
                group=cls.test_group,
                image=cls.uploaded,
            )),
        Post.objects.bulk_create(objs)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def last_page_number(
            self,
            all_posts_number: int,
            posts_per_page: int = settings.NUMBER_OF_LAST_RECORDS) -> int:
        return math.ceil(all_posts_number / posts_per_page)

    @classmethod
    def last_page_records_number(
            self,
            all_posts_number: int,
            posts_per_page: int = settings.NUMBER_OF_LAST_RECORDS) -> int:
        return (
            all_posts_number % posts_per_page
            if all_posts_number % posts_per_page != 0
            else posts_per_page
        )

    def test_posts_index_page_has_correct_number_of_records(self):
        """Check paginator: the 1st index page has correct number of posts"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']),
            settings.NUMBER_OF_LAST_RECORDS
        )

    def test_posts_index_page_has_correct_number_of_last_records(self):
        """Check paginator: the last index page has correct number of posts"""
        all_posts_number = Post.objects.count()
        response = self.authorized_client.get(
            reverse('posts:index')
            + f'?page={self.last_page_number(all_posts_number)}'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            self.last_page_records_number(all_posts_number)
        )

    def test_posts_group_list_page_has_correct_number_of_records(self):
        """Check paginator: the 1st group page has correct number of posts"""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'group_name': self.test_group.slug})
        )
        self.assertEqual(
            len(response.context['page_obj']),
            settings.NUMBER_OF_LAST_RECORDS
        )

    def test_posts_group_list_page_has_correct_number_of_last_records(self):
        """Check paginator: the last group page has correct number of posts"""
        all_group_posts_number = Post.objects.filter(
            group=self.test_group
        ).select_related(
            'group'
        ).count()
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'group_name': self.test_group.slug}
            ) + f'?page={self.last_page_number(all_group_posts_number)}'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            self.last_page_records_number(all_group_posts_number)
        )

    def test_posts_profile_page_has_correct_number_of_records(self):
        """Check paginator: the 1st profile page has correct number of posts"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(
            len(response.context['page_obj']),
            settings.NUMBER_OF_LAST_RECORDS
        )

    def test_posts_profile_page_has_correct_number_of_last_records(self):
        """Check paginator:the last profile page has correct number of posts"""
        all_profile_posts_number = Post.objects.filter(
            author=self.user
        ).select_related(
            'author'
        ).count()
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ) + f'?page={self.last_page_number(all_profile_posts_number)}'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            self.last_page_records_number(all_profile_posts_number)
        )
