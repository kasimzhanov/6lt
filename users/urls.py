from django.urls import path
from .views import (
    RegisterView,
    MeView,
    UserListView,
    UserDetailView,
    DeactivateUserView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("<int:pk>/deactivate/", DeactivateUserView.as_view(), name="deactivate"),
]