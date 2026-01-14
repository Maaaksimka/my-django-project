"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам и т.д.
"""

import logging
from os import name
from timeit import default_timer
from csv import DictWriter

from django.contrib.syndication.views import Feed
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models import QuerySet

from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from drf_spectacular.drainage import cache
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.core.cache import cache

from.common import save_csv_products, save_csv_orders
from .forms import GroupForm, ProductForm
from .models import Products, Orders, ProductImages
from .serializers import ProductsSerializer, OrdersSerializer

log = logging.getLogger(__name__)

@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Products
    Полный CRUD для сущностей товара
    """
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ('name', 'description',)
    filterset_fields = ('name', 'description', 'price', 'discount', 'archived')
    ordering_fields = ('name', 'price', 'discount',)

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = 'products-export.csv'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            'name',
            'description',
            'price',
            'discount',
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response


    @action(
        detail=False,
        methods=['post'],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request) -> Response:
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(data=products, many=True)
        return Response(serializer.data)


    @extend_schema(
        summary="Get one product by id",
        description="Retrieves **product**, return 404 if not found",
        responses={
            200: ProductsSerializer,
            404: OpenApiResponse(
                description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class OrderViewSet(ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ("user", "delivery_address",)
    filterset_fields = ("user", "delivery_address", "created_at", "promocode", "products")
    ordering_fields = ("created_at", "user",)

    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = 'orders-export.csv'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            'pk',
            'user_id',
            'promocode',
            'delivery_address',
            'products',
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        orders_data = [
            {
                "pk": str(order.pk),
                "user_id": str(order.user.id),
                "promocode": order.promocode,
                "delivery_address": order.delivery_address,
                "products": [
                    str(product.id)
                    for product in order.products.all()
                ]
            }
            for order in queryset
        ]
        writer.writerows(orders_data)

        return response


class ShopIndexView(View):

    # @method_decorator(cache_page(60 * 2))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1111),
            ('Desktop', 2222),
            ('Smartphone', 333),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 1,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")

        print("shop index context", context)
        return render(request, 'shopapp/shop-index.html', context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related("permissions").all(),
        }
        return render(request, 'shopapp/groups-list.html', context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = 'shopapp/products-details.html'
    # model = Products
    context_object_name = 'product'
    queryset = Products.objects.prefetch_related("images")


class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    # model = Products
    context_object_name = "products"
    queryset = Products.objects.filter(archived=False)


class ProductsCreateView(UserPassesTestMixin, CreateView):
    def test_func(self):
        user = self.request.user
        return self.request.user.is_superuser or user.has_perm("shopapp.add_products")
    model = Products
    # fields = '__all__'
    fields = ['name', 'description', 'price', 'discount', 'archived', "preview"]
    success_url = reverse_lazy("shopapp:products_list")
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

# class ProductsCreateView(CreateView):
#     model = Products
#     # fields = '__all__'
#     fields = ['name', 'description', 'price', 'discount', 'archived']
#     success_url = reverse_lazy("shopapp:products_list")
    # def form_valid(self, form):
    #     form.instance.created_by = self.request.user
    #     return super().form_valid(form)

class ProductsUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        user = self.request.user
        product = get_object_or_404(Products, pk=self.kwargs['pk'])
        return (self.request.user.is_staff or
                user.has_perm("shopapp.change_products")
                or product.created_by == user.pk)
    model = Products
    # fields = ['name', 'description', 'price', 'discount', 'archived', "preview"]
    template_name_suffix = '_update_form'
    form_class = ProductForm

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk}
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImages.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductsDeleteView(UserPassesTestMixin, DeleteView):
    def test_func(self):
        user = self.request.user
        product = get_object_or_404(Products, pk=self.kwargs['pk'])
        return (self.request.user.is_superuser or
                user.has_perm("shopapp.delete_products")
                or product.created_by == user)
    model = Products
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Orders.objects
        .select_related("user")
        .prefetch_related("products")
    )


class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = "shopapp/user-orders-list.html"
    context_object_name = "orders"

    def get_queryset(self):
        self.owner = get_object_or_404(User, pk=self.kwargs['user_id'])
        queryset = (
            Orders.objects
            .filter(user_id=self.owner)
            .prefetch_related("products")
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = self.owner
        return context



class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = ["shopapp.view_orders"]
    queryset = (
        Orders.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrderCreateView(CreateView):
    def test_func(self):
        user = self.request.user
        return self.request.user.is_superuser or user.has_perm("shopapp.add_orders") or self.request.user.is_staff
    model = Orders
    # fields = '__all__'
    fields = ['delivery_address', 'promocode', 'products']
    success_url = reverse_lazy("shopapp:orders_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class OrderUpdateView(UpdateView):
    model = Orders
    fields = '__all__'
    template_name_suffix = '_update_form'
    def get_success_url(self):
        return reverse(
            "shopapp:view_orders",
            kwargs={"pk": self.object.pk}
        )


class OrderDeleteView(DeleteView):
    model = Orders
    success_url = reverse_lazy("shopapp:orders_list")


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "product_data_export"
        product_data = cache.get(cache_key)
        if not product_data:
            products = Products.objects.order_by("pk").all()
            product_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, product_data, timeout=30)
        return JsonResponse({"products": product_data})


class OrdersExportView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect("shopapp:orders_list")

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = (Orders.objects.
                  select_related("user").
                  prefetch_related("products"))
        orders_data = [
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
        return JsonResponse({"orders": orders_data})



class UserOrdersExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request: HttpRequest, user_id) -> JsonResponse:
        user = get_object_or_404(User, pk=user_id)
        cache_key = f"user_orders_data_export_{user_id}"
        serializer_data = cache.get(cache_key)
        if serializer_data is None:
            orders = (
                Orders.objects
                .filter(user_id=user_id)
                .prefetch_related("products")
            )
            serializer_data = OrdersSerializer(orders, many=True)
            cache.set(cache_key, serializer_data, 300)
        return JsonResponse({"orders": serializer_data.data})



class LatestProductsFeed(Feed):
    title = "Blog new products (latest)"
    description = "Updates on changes and addition products"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return (
            Products.objects
            .filter(created_at__isnull=False)
            .order_by('-created_at')[:5]
        )

    def item_title(self, item: Products):
        return item.name

    def item_description(self, item: Products):
        return item.description[:50]
