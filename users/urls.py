from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
    UserListView,
    UserDetailView,
    DeactivateUserView,
    MeCacheView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("me/cache/", MeCacheView.as_view(), name="me-cache"),
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("<int:pk>/deactivate/", DeactivateUserView.as_view(), name="deactivate"),
]