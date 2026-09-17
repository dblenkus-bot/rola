import logging

from rest_framework import exceptions, mixins, views, viewsets, permissions, status
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

logger = logging.getLogger(__name__)


class LoginView(views.APIView):
    permission_classes = ()
    serializer_class = TokenSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token = Token.objects.create_token(user=user)

        return Response(self.serializer_class(token).data)


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

    @action(detail=False, methods=["post"])
    def activate_account(self, request):
        """Activate user account."""
        serializer = ActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response()

    @action(detail=True, methods=["post"])
    def change_password(self, request, **kwargs):
        """Change user password."""
        user = self.get_object()

        serializer = ChangePasswordSerializer(
            data=request.data, context={"user": user, "request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response()

    @action(detail=False, methods=["post"])
    def request_password_reset(self, request):
        """Request user password reset."""
        serializer = RequestPasswordResetSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response()

    @action(detail=False, methods=["post"])
    def password_reset(self, request):
        """Reset user password."""
        serializer = PasswordResetSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response()

    # @action(detail=False, methods=['post'])
    # def validate_password(self, request):
    #     """Validate user password."""
    #     serializer = ValidatePasswordSerializer(data=request.data, context={'user': request.user})
    #     serializer.is_valid()

    #     return Response(serializer.errors)
