from django.core.cache import cache
from django.conf.locale import sr

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .permissions import IsAdmin, IsOwner

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = get_tokens_for_user(user)

        return Response({
            "user": UserSerializer(user).data,
            "tokens": tokens,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        tokens = get_tokens_for_user(user)

        return Response({
            "user": UserSerializer(user).data,
            "tokens": tokens,
        })


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Успешный выход"})
        except KeyError:
            return Response(
                {"detail": "Передайте refresh токен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"detail": "Токен уже недействителен"},
                status=status.HTTP_400_BAD_REQUEST
            )


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        cache_key = f"user_{pk}"

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response({
                "cached": True,
                "data": cached_data
            })

        user = self.get_object()
        serializer = self.get_serializer(user)

        cache.set(cache_key, serializer.data, timeout=300)

        return Response({
            "cached": False,
            "data": serializer.data
        })


class MeCacheView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        cache_key = f"user_{user.pk}"

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response({
                "cached": True,
                "data": cached_data
            })

        serializer = UserSerializer(user)

        cache.set(cache_key, serializer.data, timeout=300)

        return Response({
            "cached": False,
            "data": serializer.data
        })


class DeactivateUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.is_active = False
            user.save()

            return Response({"detail": "Пользователь деактивирован"})
        except User.DoesNotExist:
            return Response(
                {"detail": "Не найден"},
                status=status.HTTP_404_NOT_FOUND
            )