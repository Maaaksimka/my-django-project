import json
from django.test import TestCase
from django.urls import reverse
# from myauth.views import get_cookie_view

class GetCookieViewTestCase(TestCase):
    def test_get_cookie_view(self):
        response = self.client.get(reverse("myauth:cookie-get"))
        self.assertContains(response, "cookie value")

class FooBarViewTestCase(TestCase):
    def test_foo_bar_view(self):
        response = self.client.get(reverse("myauth:foo-bar"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers['content-type'], 'application/json'
        )
        expected_data = {"foo": "bar", "span": "eggs"}
        # self.assertEqual(response.json(), expected_data)
        self.assertJSONEqual(response.content, expected_data)