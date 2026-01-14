from django.core.management import BaseCommand
from django.contrib.auth.models import User
from shopapp import models
from shopapp.models import Orders, Products


class Command(BaseCommand):
    def handle(self, *args, **options):
        order = Orders.objects.first()
        if not order:
            self.stdout.write("No orders found")
            return

        products = Products.objects.all()

        for product in products:
            order.products.add(product)

        order.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully added products {order.products.all()} to order {order}"))
