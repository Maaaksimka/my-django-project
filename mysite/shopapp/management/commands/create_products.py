from django.core.management import BaseCommand
from shopapp.models import Products


class Command(BaseCommand):
    """
    Create products
    """

    def handle(self, *args, **options):
        self.stdout.write("Creating products...")
        products_name = [
            "Laptop",
            "Desktop",
            "Smartphone",
        ]
        for product_name in products_name:
            product, created = Products.objects.get_or_create(name=product_name)
            self.stdout.write("Product {} created".format(product_name))


        self.stdout.write(self.style.SUCCESS("Successfully created products"))