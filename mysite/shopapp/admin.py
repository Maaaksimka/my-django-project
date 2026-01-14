from io import TextIOWrapper
from csv import DictReader

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .common import save_csv_products, save_csv_orders
from .models import Products, Orders, ProductImages
from .admin_mixins import ExportAsCSVMixin
from .forms import CSVImportForm


class OrderInline(admin.TabularInline):
    model = Products.orders.through


class ProductsInline(admin.StackedInline):
    model = ProductImages

@admin.action(description="Archive products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)

@admin.action(description="Unarchive products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "shopapp/products_changelist.html"
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
    ]
    inlines = [
        OrderInline,
        ProductsInline,
    ]
    # list_display = ('pk', 'name', 'description', 'price', 'discount')
    list_display = ('pk', 'name', 'description_short', 'price', 'discount', 'archived')
    list_display_links = ('pk', 'name',)
    ordering = ('name', '-pk',)
    search_fields = ('name', 'description', 'price', 'discount')
    fieldsets = [
        (None, {
            'fields': ('name', 'description'),
        }),
        ('Price options', {
            'fields': ('price', 'discount'),
            'classes': ('wide', 'collapse',),
        }),
        ('Images', {
            'fields': ('preview',),
        }),
        ('Extra options', {
            'fields': ('archived',),
            'classes': ('wide', 'collapse',),
            'description': 'Extra options. Field "archived" is for soft delete',
        })
    ]

    def description_short(self, obj: Products) -> str:
        if len(obj.description) < 75:
            return obj.description
        return f'{obj.description[:75]}...'

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                'form': form,
            }
            return render(request, "admin/csv_forms.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                'form': form,
            }
            return render(request, "admin/csv_forms.html", context, status=400)

        save_csv_products(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
        )
        # csv_file = TextIOWrapper(
        #     form.files["csv_file"].file,
        #     encoding=request.encoding,
        # )
        # reader = DictReader(csv_file)
        #
        # products = [
        #     Products(**row)
        #     for row in reader
        # ]
        # Products.objects.bulk_create(products)
        self.message_user(request, "Data from CSV was imported.")
        return redirect("..")


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-products-csv/",
                self.import_csv,
                name="import_products_csv",
            )
        ]
        return new_urls + urls


# admin.site.register(Products, ProductsAdmin)


class OrderProductsInline(admin.StackedInline):
    model = Orders.products.through


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "shopapp/orders_changelist.html"
    inlines = [
        OrderProductsInline,
    ]
    list_display = ("delivery_address", "promocode", "created_at", "user_verbose")

    def get_queryset(self, request):
        return Orders.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Orders) -> str:
        return obj.user.first_name or obj.user.username


    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                'form': form,
            }
            return render(request, "admin/csv_forms.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                'form': form,
            }
            return render(request, "admin/csv_forms.html", context, status=400)

        save_csv_orders(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
        )

        self.message_user(request, "Data from CSV was imported.")
        return redirect("..")


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-orders-csv/",
                self.import_csv,
                name="import_orders_csv",
            )
        ]
        return new_urls + urls
