from http import HTTPStatus

from django.test import Client, TestCase

from users.forms import User


class UserPagesURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_urls_exist_at_desired_location(self):
        """Check the existence of '/auth/.../' pages.

        Check if the HTTP status code is 'OK' for '/auth/.../' pages
        """
        urls = (
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/done/',
        )
        for url in urls:
            with self.subTest(field=url):
                self.assertEqual(
                    self.guest_client.get(url).status_code, HTTPStatus.OK
                )

    def test_users_urls_exist_at_desired_location_for_authorized(self):
        """Check the existence of '/auth/.../' pages for authorized users.

        Check if the HTTP status code is 'OK' for '/auth/.../' pages
        when authorized user is logged in
        """
        urls = (
            '/auth/password_change/',
            '/auth/password_change/done/',
            '/auth/logout/',
        )
        for url in urls:
            with self.subTest(field=url):
                self.assertEqual(
                    self.authorized_client.get(url).status_code, HTTPStatus.OK
                )

    def test_users_urls_redirect_guest_to_login_page(self):
        """ Check the guest redirection from /auth/.../ to login page.

        Check the case when the guest client trying to change password.
        He should be redirected to the login page, then (if he had logged in)
        to the password change page.
        """
        urls = (
            '/auth/password_change/',
            '/auth/password_change/done/',
        )
        for url in urls:
            with self.subTest(field=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, (f'/auth/login/?next={url}')
                )

    def test_users_url_does_not_exist(self):
        """Check the non-existence of the wrong '/auth/.../' page.

        Check if the HTTP status code is 'NOT FOUND'
        for the '/auth/unexisting_page/' page
        """
        url = ('/auth/unexisting_page/',)
        with self.subTest(field=url):
            self.assertEqual(
                self.guest_client.get(url).status_code, HTTPStatus.NOT_FOUND
            )

    def test_users_urls_use_correct_template(self):
        """Check templates for '/auth/.../' pages"""
        field_responses = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/':
                'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for field, expected_value in field_responses.items():
            with self.subTest(field=field):
                self.assertTemplateUsed(
                    self.guest_client.get(field), expected_value
                )

    def test_users_urls_use_correct_template_for_authorized(self):
        """Check templates for '/auth/.../' pages if user is authorized"""
        urls_templates = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/logout/': 'users/logout.html',
        }
        for field, expected_value in urls_templates.items():
            with self.subTest(field=field):
                self.assertTemplateUsed(
                    self.authorized_client.get(field), expected_value
                )
