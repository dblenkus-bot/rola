"""Validate account and token API payloads."""

from functools import partial

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F

from rest_framework import exceptions, serializers

from .models import Location, User, Token
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
    class Meta:
        model = Token
        fields = ["token", "expires"]

    token = serializers.CharField(source="key")


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            email=attrs.get("email"),
            password=attrs.get("password"),
        )
        if not user:
            raise serializers.ValidationError(
                "Unable to log in with provided credentials.", code="authorization"
            )

        attrs["user"] = user
        return attrs


class ActivationSerializer(serializers.Serializer):
    """Serializer for user account activation."""

    token = serializers.CharField()

    def validate(self, attrs):
        attrs["user"] = validate_activation_token(attrs["token"])
        return attrs

    def save(self):
        user = self.validated_data["user"]

        user.is_active = True
        user.save()


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing the user password."""

    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_current_password(self, current_password):
        """Validate existing password."""
        user = self.context.get("user")
        if not user.check_password(current_password):
            raise serializers.ValidationError("Incorrect current password.")

        return current_password

    def validate_new_password(self, new_password):
        """Validate new password."""
        user = self.context.get("user")
        validate_password(new_password, user)

        return new_password

    def save(self):
        """Change the password."""
        user = self.context.get("user")
        user.set_password(self.validated_data["new_password"])
        user.save()

        Token.objects.expire_for_user(user)


class RequestPasswordResetSerializer(serializers.Serializer):
    """Serializer for requesting a password reset."""

    email = serializers.EmailField()

    def save(self):
        """Send the password reset email."""
        try:
            user = User.objects.get(email=self.validated_data["email"])
        except User.DoesNotExist:
            raise exceptions.NotFound("User does not exist.")

        send_reset_email(user, self.context.get("request"))


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset."""

    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, attrs):
        user = validate_reset_token(attrs["token"])
        attrs["user"] = user

        validate_password(attrs["new_password"], user)

        return attrs

    def save(self):
        user = self.validated_data["user"]

        user.set_password(self.validated_data["new_password"])
        # Increment password reset counter (invalidates all previous tokens).
        user.password_reset_counter = F("password_reset_counter") + 1
        user.save()

        Token.objects.expire_for_user(user)
