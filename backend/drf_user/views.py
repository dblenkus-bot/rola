"""Account management endpoints."""

from rest_framework import permissions, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Token, User
from .permissions import IsSuperUser, IsTargetUser
from .serializers import (
    ActivationSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    RequestPasswordResetSerializer,
    TokenSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from .throttling import AccountThrottle, LoginThrottle


class LoginView(views.APIView):
    """Issue a token for valid account credentials."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [LoginThrottle]

    def post(self, request):
        """Validate credentials and return a token with its expiration."""
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        token = Token.objects.create_token(user=serializer.validated_data["user"])
        return Response(TokenSerializer(token).data)


class UserViewSet(viewsets.ModelViewSet):
    """Manage the current account, with administrative access for superusers."""

    lookup_field = "id"
    lookup_value_regex = (
        "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    )
    queryset = User.objects.select_related("location")
    serializer_class = UserSerializer
    permission_classes = [IsTargetUser | IsSuperUser]

    def get_serializer_class(self):
        """Use model validation for writes and nullable addresses for responses."""
        if self.action == "create":
            return UserRegistrationSerializer
        if self.action in {"update", "partial_update"}:
            return UserUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        """Limit account visibility before object lookup or serialization."""
        if (
            getattr(self, "swagger_fake_view", False)
            or not self.request.user.is_authenticated
        ):
            return self.queryset.none()
        user = self.request.user
        if self.request.query_params.get("current", False) or not user.is_superuser:
            return self.queryset.filter(pk=user.pk)
        return self.queryset

    def get_throttles(self):
        """Rate-limit account creation and recovery by caller address."""
        if self.action in {
            "create",
            "activate_account",
            "request_password_reset",
            "password_reset",
        }:
            return [AccountThrottle()]
        return super().get_throttles()

    @action(
        detail=False,
        methods=["post"],
        authentication_classes=[],
        permission_classes=[permissions.AllowAny],
    )
    def activate_account(self, request):
        """Activate an account using its email token."""
        serializer = ActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()

    @action(detail=True, methods=["post"])
    def change_password(self, request, **kwargs):
        """Change the caller's password and expire previous tokens."""
        serializer = ChangePasswordSerializer(
            data=request.data, context={"user": self.get_object(), "request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()

    @action(
        detail=False,
        methods=["post"],
        authentication_classes=[],
        permission_classes=[permissions.AllowAny],
    )
    def request_password_reset(self, request):
        """Request an account recovery email."""
        serializer = RequestPasswordResetSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()

    @action(
        detail=False,
        methods=["post"],
        authentication_classes=[],
        permission_classes=[permissions.AllowAny],
    )
    def password_reset(self, request):
        """Consume a recovery token and set a new password."""
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()
