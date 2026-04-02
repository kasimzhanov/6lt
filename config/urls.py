from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
