import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group
from users.forms import User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.test_group1 = Group.objects.create(
            title='Заголовок тестовой группы 1',
            slug='test-slug1',
            description='Описание тестовой группы 1',
        )
        cls.test_group2 = Group.objects.create(
            title='Заголовок тестовой группы 2',
            slug='test-slug2',
            description='Описание тестовой группы 2',
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
            group=cls.test_group1,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=False)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_create_post_form_check(self):
        """Check if the valid post form is creating a new post"""
        posts_before = set(Post.objects.all())
        form_data = {
            'text': 'Текст поста',
            'group': self.test_group1.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}
        ),)
        posts_after = set(Post.objects.all())
        created_post = posts_after - posts_before
        self.assertEqual(len(created_post), 1)
        post = created_post.pop()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image.size, form_data['image'].size)

    def test_posts_edit_post_form_check(self):
        """Check if the valid edit post form is editing an existing post"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.test_group2.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.test_post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.test_post.id}
        ),)
        self.assertEqual(Post.objects.count(), posts_count)
        edited_post = Post.objects.filter(id=self.test_post.id)[0]
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.author, self.user)
        self.assertEqual(edited_post.group.id, form_data['group'])

    def test_posts_forms_labels_check(self):
        """Check if form's labels are correct"""
        text_label = self.form.fields['text'].label
        group_label = self.form.fields['group'].label
        image_label = self.form.fields['image'].label
        self.assertEqual(text_label, 'Новый текст')
        self.assertEqual(group_label, 'Группа записи')
        self.assertEqual(image_label, 'Картинка')

    def test_posts_forms_help_texts_check(self):
        """Check if form's help texts are correct"""
        text_help_text = self.form.fields['text'].help_text
        group_help_text = self.form.fields['group'].help_text
        image_help_text = self.form.fields['image'].help_text
        self.assertEqual(text_help_text, 'Напишите текст записи')
        self.assertEqual(group_help_text, 'Выберите группу')
        self.assertEqual(image_help_text, 'Прикрепите картинку')
