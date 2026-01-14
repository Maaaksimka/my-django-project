from django.contrib.auth.views import LoginView
from django.urls import path
from .views import (
    get_cookie_view,
    set_cookie_view,
    get_session_view,
    set_session_view,
    MyLogoutPage,
    AboutMeView,
    RegisterView,
    FooBarView,
    AvatarUpdateView,
    UserListView,
    UserDetailView,
    HelloView,
)


app_name = "myauth"

urlpatterns = [
    path('login/',
         LoginView.as_view(
             template_name="myauth/login.html",
             redirect_authenticated_user=True,
         ),
         name="login"),

    path("hello/", HelloView.as_view(), name="hello"),

    path('logout/', MyLogoutPage.as_view(), name="logout"),
    path('about-me/', AboutMeView.as_view(), name="about-me"),
    path('avatar-update/<int:pk>', AvatarUpdateView.as_view(), name="avatar_update"),
    path('register/', RegisterView.as_view(), name="register"),
    path('users/', UserListView.as_view(), name="users_list"),
    path('users/<int:pk>', UserDetailView.as_view(), name="profile-details"),
    path('cookie/get/', get_cookie_view, name="cookie-get"),
    path('cookie/set/', set_cookie_view, name="cookie-set"),

    path('session/get/', get_session_view, name="session-get"),
    path('session/set/', set_session_view, name="session-set"),
    path('foo-bar/', FooBarView.as_view(), name="foo-bar"),

]

