"""Validate account and token API payloads."""

from functools import partial

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import models, transaction
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from .models import Location, Token, User
from .utils.signing import (
    send_activation_email,
    send_reset_email,
    validate_activation_token,
    validate_reset_token,
)


class LocationSerializer(serializers.ModelSerializer):
    """Validate postal address fields against the location model."""

    class Meta:
        """Define the writable address fields."""

        model = Location
        fields = ["address", "city", "postal_code", "country"]


class UserSerializer(serializers.ModelSerializer):
    """Expose a public profile with an embedded postal address."""

    address = serializers.CharField(source="location.address", allow_null=True)
    city = serializers.CharField(source="location.city", allow_null=True)
    postal_code = serializers.CharField(source="location.postal_code", allow_null=True)
    country = serializers.CharField(source="location.country", allow_null=True)

    class Meta:
        """Define the public account fields."""

        model = User
        fields = [
            "id",
            "password",
            "email",
            "first_name",
            "last_name",
            "address",
            "city",
            "postal_code",
            "country",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "password": {"write_only": True, "trim_whitespace": False},
        }


class NormalizedEmailField(serializers.EmailField):
    """Normalize email domains before field validators check uniqueness."""

    def to_internal_value(self, data):
        """Parse the address using the account manager's normalization rules."""
        return User.objects.normalize_email(super().to_internal_value(data))


class UserWriteSerializer(UserSerializer):
    """Validate profile writes while retaining the flat account representation."""

    serializer_field_mapping = {
        **serializers.ModelSerializer.serializer_field_mapping,
        models.EmailField: NormalizedEmailField,
    }

    def get_fields(self):
        """Use model-derived address fields for profile input."""
        fields = super().get_fields()
        for name, field in LocationSerializer().fields.items():
            field.source = f"location.{name}"
            fields[name] = field
        return fields

    def to_representation(self, instance):
        """Return nullable address fields through the profile response serializer."""
        return UserSerializer(instance, context=self.context).data

    def validate(self, attrs):
        """Validate password context and complete address writes."""
        if self.instance is not None and "password" in attrs:
            raise serializers.ValidationError(
                {"password": "Use the change-password endpoint."}
            )
        location = attrs.get("location", {})
        if self.instance is not None and self.instance.location_id is None and location:
            LocationSerializer(data=location).is_valid(raise_exception=True)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create an inactive account and email it after the transaction commits."""
        location = Location.objects.create(**validated_data.pop("location"))
        user = User.objects.create_user(location=location, **validated_data)
        transaction.on_commit(
            partial(send_activation_email, user, self.context["request"])
        )
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update profile and location together without changing credentials."""
        location_data = validated_data.pop("location", None)
        if location_data:
            if instance.location_id is None:
                instance.location = Location.objects.create(**location_data)
            else:
                for field, value in location_data.items():
                    setattr(instance.location, field, value)
                instance.location.save(update_fields=list(location_data))
        return super().update(instance, validated_data)


@extend_schema_serializer(component_name="User")
class UserRegistrationSerializer(UserWriteSerializer):
    """Validate a new account, including its required password."""

    def validate(self, attrs):
        """Check the password against the submitted account details."""
        attrs = super().validate(attrs)
        user = User(
            **{key: attrs.get(key) for key in ("email", "first_name", "last_name")}
        )
        try:
            validate_password(attrs["password"], user)
        except ValidationError as error:
            raise serializers.ValidationError({"password": error.messages}) from error
        return attrs


class UserUpdateSerializer(UserWriteSerializer):
    """Update a profile without replacing its verified email or password."""

    class Meta(UserWriteSerializer.Meta):
        """Make credentials optional and document their update restrictions."""

        extra_kwargs = {
            **UserWriteSerializer.Meta.extra_kwargs,
            "password": {
                "write_only": True,
                "required": False,
                "help_text": "Must be omitted; use the change-password endpoint.",
            },
            "email": {
                "required": False,
                "validators": [],
                "help_text": "Immutable after registration; omit or send the current address.",
            },
        }

    def validate_email(self, email):
        """Reject changes to the account's verified address."""
        if email != self.instance.email:
            raise serializers.ValidationError("The email address cannot be changed.")
        return email


class TokenSerializer(serializers.ModelSerializer):
    """Represent a newly issued token and its expiration."""

    token = serializers.CharField(source="key", read_only=True)

    class Meta:
        """Define the login response."""

        model = Token
        fields = ["token", "expires"]
        read_only_fields = ["expires"]


class LoginSerializer(serializers.Serializer):
    """Authenticate an active account."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        """Verify credentials without revealing account existence."""
        user = authenticate(request=self.context.get("request"), **attrs)
        if not user:
            raise serializers.ValidationError(
                "Unable to log in with provided credentials.", code="authorization"
            )
        attrs["user"] = user
        return attrs


class ActivationSerializer(serializers.Serializer):
    """Activate the account referenced by a signed token."""

    token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Require an unexpired token for an inactive account."""
        validate_activation_token(attrs["token"])
        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        """Consume an activation token exactly once."""
        user = validate_activation_token(self.validated_data["token"], lock=True)
        user.is_active = True
        user.save(update_fields=["is_active"])
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Validate a credential change against the current password."""

    current_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_current_password(self, current_password):
        """Require the account's existing password."""
        if not self.context["user"].check_password(current_password):
            raise serializers.ValidationError("Incorrect current password.")
        return current_password

    def validate_new_password(self, new_password):
        """Apply the configured password validators."""
        validate_password(new_password, self.context["user"])
        return new_password

    @transaction.atomic
    def save(self, **kwargs):
        """Replace the password and revoke outstanding login and reset tokens."""
        user = User.objects.select_for_update().get(pk=self.context["user"].pk)
        if not user.check_password(self.validated_data["current_password"]):
            raise serializers.ValidationError(
                {"current_password": "Incorrect current password."}
            )
        user.set_password(self.validated_data["new_password"])
        user.password_reset_counter += 1
        user.save(update_fields=["password", "password_reset_counter"])
        Token.objects.expire_for_user(user)
        return user


class RequestPasswordResetSerializer(serializers.Serializer):
    """Request recovery without exposing whether an account exists."""

    email = serializers.EmailField()

    def save(self, **kwargs):
        """Send a recovery message only for an active account."""
        user = User.objects.filter(
            email=self.validated_data["email"], is_active=True
        ).first()
        if user is not None:
            transaction.on_commit(
                partial(send_reset_email, user, self.context["request"])
            )
        return user


class PasswordResetSerializer(serializers.Serializer):
    """Validate a signed recovery token and replacement password."""

    token = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        """Check the token and password policy before changing credentials."""
        user = validate_reset_token(attrs["token"])
        validate_password(attrs["new_password"], user)
        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        """Consume the recovery token and revoke all login tokens atomically."""
        user = validate_reset_token(self.validated_data["token"], lock=True)
        user.set_password(self.validated_data["new_password"])
        user.password_reset_counter += 1
        user.save(update_fields=["password", "password_reset_counter"])
        Token.objects.expire_for_user(user)
        return user
