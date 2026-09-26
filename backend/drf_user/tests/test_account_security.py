"""Exercise credential and account isolation boundaries."""

from datetime import timedelta
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import pytest
from django.core import mail, signing
from django.test import override_settings
from django.urls import reverse
from django.utils.timezone import now
from rest_framework.test import APIClient

from drf_user.models import Location, Token, User
from drf_user.serializers import PasswordResetSerializer
from drf_user.utils.signing import PASSWORD_RESET_SALT, generate_reset_token


@pytest.fixture
def account(db):
    """Create an active account with an independent login credential."""
    return User.objects.create_user(
        email="person@example.com", password="Original!73", is_active=True
    )


@pytest.fixture
def client(account):
    """Authenticate API calls as the fixture account."""
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Token {Token.objects.create_token(user=account).key}"
    )
    return client


@pytest.fixture
def address():
    """Provide a complete postal address for account writes."""
    return {
        "address": "Street 1",
        "city": "Ljubljana",
        "postal_code": "1000",
        "country": "SI",
    }


def test_profile_password_write_is_rejected(client, account):
    response = client.patch(
        reverse("user-detail", kwargs={"id": account.id}),
        {"password": "Replacement!73"},
    )
    assert response.status_code == 400
    account.refresh_from_db()
    assert account.check_password("Original!73")


def test_location_creation_and_partial_update_are_atomic(client, account, address):
    url = reverse("user-detail", kwargs={"id": account.id})
    response = client.get(url)
    assert response.status_code == 200
    assert {field: response.data[field] for field in address} == dict.fromkeys(address)
    assert "location" not in response.data

    response = client.patch(url, {"first_name": "Initial"})
    assert response.status_code == 200
    assert {field: response.data[field] for field in address} == dict.fromkeys(address)
    assert not Location.objects.exists()

    response = client.patch(url, {"city": "Ljubljana"})
    assert response.status_code == 400
    assert set(response.data) == {"address", "postal_code", "country"}
    assert Location.objects.count() == 0
    response = client.patch(url, address)
    assert response.status_code == 200
    assert {field: response.data[field] for field in address} == address
    response = client.patch(url, {"city": "Maribor", "first_name": "Changed"})
    assert response.status_code == 200
    updated_address = {**address, "city": "Maribor"}
    assert {field: response.data[field] for field in address} == updated_address
    account.refresh_from_db()
    assert {
        field: getattr(account.location, field) for field in address
    } == updated_address
    assert account.first_name == "Changed"
    assert Location.objects.count() == 1


@pytest.mark.parametrize("field", ["address", "city", "postal_code", "country"])
@pytest.mark.parametrize(
    ("value", "code"),
    [("x" * 101, "max_length"), (None, "null")],
    ids=["too_long", "null"],
)
def test_invalid_address_field_does_not_update_profile(
    client, account, address, field, value, code
):
    account.location = Location.objects.create(**address)
    account.save(update_fields=["location"])

    response = client.patch(
        reverse("user-detail", kwargs={"id": account.id}),
        {field: value, "first_name": "Changed"},
        format="json",
    )

    assert response.status_code == 400
    assert set(response.data) == {field}
    assert response.data[field][0].code == code
    account.refresh_from_db()
    assert account.first_name is None
    assert {field: getattr(account.location, field) for field in address} == address
    assert Location.objects.count() == 1


@pytest.mark.parametrize(("length", "status"), [(100, 201), (101, 400)])
def test_registration_validates_address_lengths(db, address, length, status):
    address = dict.fromkeys(address, "x" * length)
    response = APIClient().post(
        reverse("user-list"),
        {
            "email": "new@example.com",
            "password": "Original!73",
            "first_name": "New",
            "last_name": "Account",
            **address,
        },
        format="json",
    )

    assert response.status_code == status
    if status == 201:
        assert {field: response.data[field] for field in address} == address
        location = User.objects.get().location
        assert {field: getattr(location, field) for field in address} == address
    else:
        assert set(response.data) == set(address)
        assert all(errors[0].code == "max_length" for errors in response.data.values())
        assert not User.objects.exists()
        assert not Location.objects.exists()


def test_registration_validation_does_not_leave_an_address(db):
    payload = {
        "email": "new@example.com",
        "password": "short",
        "first_name": "New",
        "last_name": "Account",
        "address": "Street 1",
        "city": "Ljubljana",
        "postal_code": "1000",
        "country": "SI",
    }
    response = APIClient().post(reverse("user-list"), payload)
    assert response.status_code == 400
    assert not Location.objects.exists()
    assert not User.objects.exists()


def test_registration_password_is_checked_against_submitted_name(db, address):
    response = APIClient().post(
        reverse("user-list"),
        {
            "email": "new@example.com",
            "password": "Original!73",
            "first_name": "Original!73",
            "last_name": "Account",
            **address,
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data == {
        "password": ["The password is too similar to the first name."]
    }
    assert not User.objects.exists()
    assert not Location.objects.exists()


def test_password_change_revokes_login_and_recovery_tokens(client, account):
    reset_token = generate_reset_token(account)
    response = client.post(
        reverse("user-change-password", kwargs={"id": account.id}),
        {"current_password": "Original!73", "new_password": "Replacement!73"},
    )
    assert response.status_code == 200
    assert all(token.is_expired for token in account.auth_tokens.all())
    response = APIClient().post(
        reverse("user-password-reset"),
        {"token": reset_token, "new_password": "Another!73"},
    )
    assert response.status_code == 400


def test_validated_recovery_token_cannot_be_replayed(account):
    data = {"token": generate_reset_token(account), "new_password": "Replacement!73"}
    first = PasswordResetSerializer(data=data)
    second = PasswordResetSerializer(data=data)
    first.is_valid(raise_exception=True)
    second.is_valid(raise_exception=True)
    first.save()
    from rest_framework.exceptions import ValidationError

    with pytest.raises(ValidationError, match="Bad token"):
        second.save()


def test_recovery_does_not_reveal_unknown_or_inactive_accounts(
    account, django_capture_on_commit_callbacks
):
    client = APIClient()
    with django_capture_on_commit_callbacks(execute=True):
        active = client.post(
            reverse("user-request-password-reset"), {"email": account.email}
        )
        unknown = client.post(
            reverse("user-request-password-reset"), {"email": "unknown@example.com"}
        )
        account.is_active = False
        account.save(update_fields=["is_active"])
        inactive = client.post(
            reverse("user-request-password-reset"), {"email": account.email}
        )
    assert active.status_code == unknown.status_code == inactive.status_code == 200
    assert active.data == unknown.data == inactive.data
    assert len(mail.outbox) == 1


def test_recovery_email_uses_configured_frontend(
    account, django_capture_on_commit_callbacks
):
    with (
        override_settings(ROLA_FRONTEND_URL="https://photos.example.com"),
        django_capture_on_commit_callbacks(execute=True),
    ):
        response = APIClient().post(
            reverse("user-request-password-reset"), {"email": account.email}
        )
    assert response.status_code == 200
    link = next(
        line for line in mail.outbox[0].body.splitlines() if line.startswith("https://")
    )
    assert link.startswith("https://photos.example.com/password-reset?")
    assert parse_qs(urlsplit(link).query)["token"]


@pytest.mark.parametrize(
    "payload", [None, {}, {"email": [], "counter": 0}, {"email": "x", "counter": True}]
)
def test_signed_malformed_recovery_payload_returns_validation_error(db, payload):
    response = APIClient().post(
        reverse("user-password-reset"),
        {
            "token": signing.dumps(payload, salt=PASSWORD_RESET_SALT),
            "new_password": "Replacement!73",
        },
    )
    assert response.status_code == 400


def test_expired_login_tokens_are_rejected(account):
    token = Token.objects.create_token(
        user=account, expires=now() - timedelta(seconds=1)
    )
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    assert client.get(reverse("user-list")).status_code == 401
    account.is_active = False
    account.save(update_fields=["is_active"])
    token.expires = now() + timedelta(days=1)
    token.save(update_fields=["expires"])
    assert client.get(reverse("user-list")).status_code == 401


def test_authentication_endpoints_are_rate_limited(db):
    from drf_user.throttling import LoginThrottle

    with patch.object(LoginThrottle, "rate", "1/hour", create=True):
        client = APIClient()
        assert (
            client.post(
                reverse("login"), {"email": "nobody@example.com", "password": "wrong"}
            ).status_code
            == 400
        )
        assert (
            client.post(
                reverse("login"), {"email": "nobody@example.com", "password": "wrong"}
            ).status_code
            == 429
        )


def test_nullable_names_and_user_clean_are_safe(account):
    account.first_name = None
    account.last_name = None
    account.clean()
    assert account.get_full_name() == ""
    assert account.get_short_name() == ""


def test_malformed_account_id_does_not_reach_uuid_lookup(client):
    response = client.get("/api/v1/user/------------------------------------")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "email", ["person@example.com", "person@Example.com", "PERSON@example.com"]
)
def test_registration_rejects_normalized_duplicate_email(account, address, email):
    response = APIClient().post(
        reverse("user-list"),
        {
            "email": email,
            "password": "Original!73",
            "first_name": "New",
            "last_name": "Account",
            **address,
        },
        format="json",
    )
    assert response.status_code == 400
    assert set(response.data) == {"email"}
    assert User.objects.count() == 1
    assert not Location.objects.exists()


def test_profile_put_does_not_require_credentials(client, account, address):
    response = client.put(
        reverse("user-detail", kwargs={"id": account.id}),
        {"first_name": "Updated", "last_name": "Account", **address},
        format="json",
    )
    assert response.status_code == 200
    account.refresh_from_db()
    assert account.first_name == "Updated"
    assert account.location.city == address["city"]
    assert account.email == "person@example.com"
    assert account.check_password("Original!73")


@pytest.mark.parametrize("method", ["put", "patch"])
def test_profile_rejects_email_changes_atomically(client, account, address, method):
    response = getattr(client, method)(
        reverse("user-detail", kwargs={"id": account.id}),
        {
            "email": "changed@example.com",
            "first_name": "Changed",
            "last_name": "Account",
            **address,
        },
        format="json",
    )
    assert response.status_code == 400
    assert set(response.data) == {"email"}
    account.refresh_from_db()
    assert account.email == "person@example.com"
    assert account.first_name is None
    assert not Location.objects.exists()


def test_profile_accepts_unchanged_normalized_email(client, account):
    response = client.patch(
        reverse("user-detail", kwargs={"id": account.id}),
        {"email": "Person@Example.com", "first_name": "Updated"},
    )
    assert response.status_code == 200
    account.refresh_from_db()
    assert account.email == "person@example.com"
    assert account.first_name == "Updated"


@pytest.mark.parametrize("stored_email", ["person@example.com", "Person@Example.com"])
def test_registration_checks_uniqueness_against_stored_case(
    account, address, stored_email
):
    User.objects.filter(pk=account.pk).update(email=stored_email)
    response = APIClient().post(
        reverse("user-list"),
        {
            "email": "PERSON@EXAMPLE.COM",
            "password": "Original!73",
            "first_name": "New",
            "last_name": "Account",
            **address,
        },
        format="json",
    )
    assert response.status_code == 400
    assert set(response.data) == {"email"}
    assert User.objects.count() == 1
    assert not Location.objects.exists()


def test_registration_lowercases_email_without_removing_dots_or_tags(db, address):
    response = APIClient().post(
        reverse("user-list"),
        {
            "email": "Person.Name+Contest@Example.com",
            "password": "Original!73",
            "first_name": "New",
            "last_name": "Account",
            **address,
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.data["email"] == "person.name+contest@example.com"
    assert User.objects.get().email == "person.name+contest@example.com"


@pytest.mark.parametrize("method", ["create_user", "create_superuser"])
def test_account_manager_normalizes_email(db, method):
    user = getattr(User.objects, method)(
        email="Person.Name+Contest@Example.com", password="Original!73"
    )
    user.refresh_from_db()
    assert user.email == "person.name+contest@example.com"
