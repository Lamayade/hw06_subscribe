from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def test_about_author_page_accessible_by_name(self):
        """Check the access to the '/about/author/' page.

        Check if the HTTP status code is 'OK' for the '/about/author/' page,
        which bonded with the AboutAuthorView
        """
        response = self.client.get(reverse('about:author'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_author_page_uses_correct_template(self):
        """Check the template for '/about/author/' page.

        Check if the 'about/author.html' template is bonded with the
        AboutAuthorView
        """
        response = self.client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')

    def test_about_tech_page_accessible_by_name(self):
        """Check the access to the '/about/tech/' page.

        Check if the HTTP status code is 'OK' for the '/about/tech/' page,
        which bonded with the AboutTechView
        """
        response = self.client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_page_uses_correct_template(self):
        """Check the template for '/about/tech/' page.

        Check if the 'about/tech.html' template is bonded with the
        AboutTechView
        """
        response = self.client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')
