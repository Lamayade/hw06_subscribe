from http import HTTPStatus

from django.test import TestCase


class StaticPagesURLTests(TestCase):
    def test_about_urls_exist_at_desired_location(self):
        """Check the existence of '/about/.../' pages.

        Check if the HTTP status code is 'OK' for '/about/.../' pages
        """
        urls = (
            '/about/author/',
            '/about/tech/',
        )
        for url in urls:
            with self.subTest(field=url):
                self.assertEqual(
                    self.client.get(url).status_code, HTTPStatus.OK
                )

    def test_about_wrong_url_does_not_exist(self):
        """Check the non-existence of the wrong '/about/.../' page.

        Check if the HTTP status code is 'NOT FOUND'
        for the '/about/unexisting_page/' page
        """
        url = '/about/unexisting_page/'
        self.assertEqual(
            self.client.get(url).status_code, HTTPStatus.NOT_FOUND
        )

    def test_about_urls_use_correct_template(self):
        """Check templates for '/about/.../' pages"""
        urls_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for field, expected_value in urls_templates.items():
            with self.subTest(field=field):
                self.assertTemplateUsed(
                    self.client.get(field), expected_value
                )
