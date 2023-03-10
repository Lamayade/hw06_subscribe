from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import User


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_pages_use_correct_templates(self):
        """Check templates for '/users/.../' pages.

        Check if the 'users/... .html' template is bonded with the
        users: ... name
        """
        templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_users_signup_page_shows_correct_context(self):
        """Check if fields of signup page form are correct"""
        response = self.authorized_client.get(
            reverse('users:signup')
        )
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
