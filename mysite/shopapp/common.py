from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Products, Orders


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Products(**row)
        for row in reader
    ]
    Products.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding,
    )
    reader = DictReader(csv_file)

    orders = []
    for row in reader:
        order = Orders.objects.create(
            delivery_address=row["delivery_address"],
            promocode=row["promocode"],
            user_id=row["user_id"],
        )
        id_products_list = row["products"].split(",")
        products = Products.objects.filter(id__in=id_products_list)
        order.save()
        order.products.set(products)
        orders.append(order)

    return orders