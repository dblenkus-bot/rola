"""User models."""

import logging
import secrets
import uuid

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.db import models
from django.db.models.functions import Lower
from django.utils.timezone import now

from .settings import drf_user_settings

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    """Manager for User model."""

    @classmethod
    def normalize_email(cls, email: str) -> str:
        """Lowercase the address without changing dots or plus tags."""
        return super().normalize_email(email).lower()

    def _create_user(self, email, password, **extra_fields):
        """Create and save a user with the given email, and password."""
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password is not None:
            validate_password(password, user)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create a user."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class Email(models.Model):
    """E-mail model."""

    subject = models.CharField(max_length=100)

    body = models.TextField()

    html_body = models.TextField(null=True, blank=True)

    def send(self, address):
        """Send email to give address."""
        subject = "".join(self.subject.splitlines())

        email_kwargs = {}
        if self.html_body:
            email_kwargs["html_message"] = self.html_body

        try:
            send_mail(
                subject,
                self.body,
                from_email=None,
                recipient_list=[address],
                **email_kwargs,
            )
        except Exception as error:
            logger.error("Unable to send contest email (%s).", type(error).__name__)


class Location(models.Model):
    """Location model."""

    address = models.CharField(max_length=100)

    city = models.CharField(max_length=100)

    postal_code = models.CharField(max_length=100)

    country = models.CharField(max_length=100)

    def __str__(self):
        """String representation of the object."""
        return f"{self.address}, {self.postal_code} {self.city}, {self.country}"


class User(AbstractBaseUser, PermissionsMixin):
    """User model."""

    internal_id = models.AutoField(primary_key=True)

    id = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, db_index=True
    )

    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=150, null=True, blank=True)

    last_name = models.CharField(max_length=150, null=True, blank=True)

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, null=True, blank=True
    )

    is_staff = models.BooleanField(default=False)

    is_superuser = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    password_reset_counter = models.IntegerField(default=0)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    class Meta:
        """User's meta options."""

        swappable = "AUTH_USER_MODEL"
        ordering = ("internal_id",)
        constraints = [
            models.UniqueConstraint(Lower("email"), name="drf_user_email_ci_unique")
        ]

    def clean(self):
        """Clean the model."""
        super().clean()
        self.email = type(self).objects.normalize_email(self.email)

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        return " ".join(filter(None, (self.first_name, self.last_name)))

    def get_short_name(self):
        """Return the short name for the user."""
        return (self.first_name or "").strip()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(
            subject,
            message,
            from_email=from_email,
            recipient_list=[self.email],
            **kwargs,
        )


class TokenManager(models.Manager):
    """Manager for Token model."""

    def create_token(self, **kwargs):
        """Issue a token using the configured expiry unless explicitly supplied."""
        if "expires" not in kwargs:
            kwargs["expires"] = now() + drf_user_settings.TOKEN_EXPIRES_SECONDS

        return self.create(**kwargs)

    def expire_for_user(self, user):
        """Expire all tokens for the given user."""
        self.filter(user=user).update(expires=now())


class Token(models.Model):
    """Authorization token model."""

    key = models.CharField(max_length=40, primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="auth_tokens", on_delete=models.CASCADE
    )

    created = models.DateTimeField(auto_now_add=True)

    expires = models.DateTimeField()

    objects = TokenManager()

    def save(self, *args, **kwargs):
        """Generate the key if it doesn't exist and save the model."""
        if not self.key:
            self.key = secrets.token_hex(20)
        return super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Return whether the token has reached its expiry."""
        return self.expires <= now()

    def __str__(self):
        """Return string representation of the model."""
        return f"Token issued {self.created}"
