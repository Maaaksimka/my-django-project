from random import random

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, reverse, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.utils.translation import gettext_lazy as _, ngettext
from django.views.decorators.cache import cache_page

from .models import Profile

class HelloView(View):
    welcome_message = _("Welcome hello world!")
    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"<p>{products_line}</p>"
        )


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    # success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password
        )
        login(request=self.request, user=user)

        return response

    def get_success_url(self):
        return reverse(
            "myauth:about-me",
            kwargs={"pk": self.object.pk}
        )


class UserDetailView(DetailView):
    template_name = "myauth/profile-details.html"
    permission_required = ["myauth:profile-details"]
    queryset = (
        User.objects
        .select_related("profile")
    )
    context_object_name = "user"


class AvatarUpdateView(UserPassesTestMixin, UpdateView):
    model = Profile
    fields = ['avatar',]
    # fields = "__all__"
    template_name = "myauth/avatar-update.html"

    def test_func(self):
        obj = self.get_object()
        return self.request.user.pk == obj.user_id or self.request.user.is_staff

    def get_success_url(self):
        return reverse(
            "myauth:profile-details",
            kwargs={"pk": self.object.user_id}
        )


class MyLogoutPage(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect("myauth:login")


class UserListView(ListView):
    template_name = "myauth/user-list.html"
    model = User
    context_object_name = "users"


def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response

# @user_passes_test(lambda u: u.is_superuser)
@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"cookie value: {value!r} + {random()}")

@permission_required("shopapp.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set")

@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default value")
    return HttpResponse(f"Session value: {value!r}")

class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "span": "eggs"})