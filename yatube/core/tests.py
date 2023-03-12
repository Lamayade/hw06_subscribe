from http import HTTPStatus

from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_page_has_correct_http_status(self):
        '''Check if custom error page has correct HTTP status'''
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_error_page_uses_correct_template(self):
        '''Check if custom error page uses correct template'''
        response = self.client.get('/nonexist-page/')
        self.assertTemplateUsed(response, 'core/404.html')
