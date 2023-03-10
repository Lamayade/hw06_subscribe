from django.test import Client, TestCase
from django.urls import reverse

from users.forms import CreationForm
from posts.models import Post
from users.forms import User


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.test_post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )
        cls.form = CreationForm()

    def setUp(self):
        self.guest_client = Client()

    def test_users_signup_form_check(self):
        """Check signup form: the creation of a new user"""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Test',
            'last_name': 'Test',
            'username': 'test',
            'password1': 'NotUsualPassword4444',
            'password2': 'NotUsualPassword4444',
            'email': 'newuser123@test.com',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:index',
        ),)
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='test',
            ).exists()
        )
