from itertools import product
from random import choices
from string import ascii_letters

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Products, Orders
from shopapp.utils import add_two_numbers

class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_name = "".join(choices(ascii_letters, k=10))
        cls.user = User.objects.create(username="testuser", password="qwerty", is_superuser=True)
        cls.product = Products.objects.all()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.product.delete()
        super().setUpClass()


    def setUp(self):
        # self.client.login(**self.credentials)
        self.client.force_login(self.user)


    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "description": "A good table",
                "price": "123.45",
                "discount": "10",
                "archived": False,
            }
        )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Products.objects.filter(name=self.product_name).exists()
        )


class ProductDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="testuser", password="qwerty")
        cls.product = Products.objects.create(name="Best Product", price="123.45", created_by_id=1)

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()
        cls.user.delete()
        super().setUpClass()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)

class ProductListViewTestVase(TestCase):

    fixtures = [
        "groups-fixture.json",
        "user-groups-fixture.json",
        "users-fixture.json",
        "products-fixture.json",
    ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"))
        self.assertQuerySetEqual(
            qs=Products.objects.filter(archived=False).all(),
            values=[p.pk for p in response.context["products"]],
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, "shopapp/products-list.html")


class OrdersListViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # cls.credentials = dict(username="testuser", password="qwerty")
        # cls.user = User.objects.create_user(**cls.credentials)
        cls.user = User.objects.create_user(username="test_user", password="qwerty")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().setUpClass()

    def setUp(self):
        # self.client.login(**self.credentials)
        self.client.force_login(self.user)

    def test_orders_list(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):

    fixtures = ["products-fixture.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user", password="qwerty")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().setUpClass()

    def test_get_products_view(self):
        response = self.client.get(
            reverse("shopapp:products_export")
        )
        self.assertEqual(response.status_code, 200)
        products = Products.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data,
        )


class OrderCreateViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="testuser", password="qwerty", is_superuser=True)
        cls.product = Products.objects.create(name="Best Product", created_by_id=1)

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()
        cls.user.delete()
        super().setUpClass()

    def setUp(self):
        self.client.force_login(self.user)

    def test_create_order(self):
        response = self.client.post(
            reverse("shopapp:order_create"),
            {
                "delivery_address": "My Delivery Address",
                "promocode": "SALE123",
                "products": (self.product.pk, self.product.name),
                "user": self.user.username,
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, "My Delivery Address")



class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="testuser", password="qwerty", is_superuser=True)
        cls.order = Orders.objects.create(
            delivery_address="My Delivery Address",
            promocode="SALE1234",
            user=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        cls.order.delete()
        cls.user.delete()
        super().setUpClass()

    def setUp(self):
        self.client.force_login(self.user)

    def test_order_detail(self):
        response = self.client.get(reverse("shopapp:view_orders", kwargs={"pk": self.order.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Delivery Address")
        self.assertContains(response, "SALE1234")
        self.assertTrue(
            Orders.objects.filter(pk=self.order.pk).exists()
        )


class OrdersExportTestCase(TestCase):
    fixtures = [
        "groups-fixture.json",
        "user-groups-fixture.json",
        "users-fixture.json",
        "products-fixture.json",
        "orders-fixture.json",

    ]
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="test_user", password="qwerty", is_staff=True)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().setUpClass()

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_orders_view(self):
        response = self.client.get(
            reverse("shopapp:orders_export")
        )
        self.assertEqual(response.status_code, 200)
        orders = (Orders.objects.
                  select_related("user").
                  prefetch_related("products"))
        expected_data = [
            {
                "pk": order.pk,
                "user_id": order.user.id,
                # "user_name": order.user.username,
                "promocode": order.promocode,
                "delivery_address": order.delivery_address,
                "products": [
                    {
                        "name": product.name,
                        "price": float(product.price),
                    }
                    for product in order.products.all()
                ]
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(
            orders_data["orders"],
            expected_data,
        )

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)
