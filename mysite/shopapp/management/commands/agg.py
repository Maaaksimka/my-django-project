from django.core.management import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count,Sum
from django.db.models.expressions import result

from shopapp.models import Products, Orders


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Start demo aggregate")

        # result = Products.objects.filter(
        #     name__contains="Smartphone",
        # ).aggregate(
        #     Avg('price'),
        #     Max('price'),
        #     min_price=Min('price'),
        #     count=Count('id'),
        # )
        # print(result)
        orders = Orders.objects.annotate(
            total=Sum("products__price", default=0),
            products_count=Count("products"),
        )
        for order in orders:
            print(
                f"Order #{order.id}"
                f"with {order.products_count}"
                f"products worth {order.total}"
            )
        self.stdout.write(f"Done")