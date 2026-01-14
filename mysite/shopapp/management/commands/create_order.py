from typing import Sequence

from django.core.management import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from shopapp.models import Orders, Products


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Creating order with products")
        user = User.objects.get(username="adminn")
        # products: Sequence[Products] = Products.objects.defer("description", "price", "created_at").all()
        products: Sequence[Products] = Products.objects.only("id").all()
        order, created = Orders.objects.get_or_create(
            delivery_address = "ul Ivanova, d 7",
            promocode = "promo5",
            user = user,
        )
        for product in products:
            order.products.add(product)
        order.save()
        self.stdout.write(f"Order {order} created")
