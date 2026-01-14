from django.contrib.auth.models import User
from django.core.management import BaseCommand

from shopapp.models import Products


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Start demo bulk actions")

        result = Products.objects.filter(
            name__contains="Smartphone"
        ).update(discount=10)

        print(result)
        # info = [
        #     ('Smartphone 1', 199),
        #     ('Smartphone 1', 299),
        #     ('Smartphone 1', 399),
        # ]
        # products = [
        #     Products(name=name, price=price)
        #     for name, price in info
        # ]
        #
        # result = Products.objects.bulk_create(products)
        # for obj in result:
        #     print(obj)

        self.stdout.write(f"Done")