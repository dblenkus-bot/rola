import re
import time
from unittest.mock import Mock, patch
from urllib.parse import unquote

from django.core import mail
from django.db.models import F
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from drf_user.models import Token, User
from drf_user.settings import drf_user_settings
from drf_user.utils.signing import generate_activation_token, generate_reset_token


class UserManagementTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ADMIN_EMAIL = "admin@example.com"
        cls.ADMIN_PASSWORD = "p4ssWord123"
        cls.admin = User.objects.create_superuser(
            email=cls.ADMIN_EMAIL, password=cls.ADMIN_PASSWORD
        )
        cls.admin_token = Token.objects.create_token(user=cls.admin)

        cls.USER_EMAIL = "user@example.com"
        cls.USER_PASSWORD = "pa55word!"
        cls.user = User.objects.create_user(
            first_name="Klemen",
            last_name="Krajnc",
            email=cls.USER_EMAIL,
            password=cls.USER_PASSWORD,
            is_active=True,
        )
        cls.user_token = Token.objects.create_token(user=cls.user)

        cls.post_data = {
            "first_name": "Janez",
            "last_name": "Novak",
            "email": "janez@example.com",
            "password": "p4ssWord123",
            "address": "Test Street 1",
            "city": "Ljubljana",
            "postal_code": "1000",
            "country": "SI",
        }

        cls.list_url = reverse("user-list")
        cls.user_detail_url = reverse("user-detail", kwargs={"id": cls.user.id})
        cls.admin_detail_url = reverse("user-detail", kwargs={"id": cls.admin.id})
        cls.activate_account_url = reverse("user-activate-account")

    def test_list_anonymouse(self):
        response = self.client.get(self.list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_list_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token.key}")

        response = self.client.get(self.list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        result = response.data["results"][0]
        self.assertCountEqual(
            result.keys(),
            [
                "id",
                "first_name",
                "last_name",
                "email",
                "address",
                "city",
                "postal_code",
                "country",
            ],
        )
        self.assertEqual(result["id"], str(self.user.id))
        self.assertEqual(result["email"], self.user.email)
        self.assertEqual(result["first_name"], self.user.first_name)
        self.assertEqual(result["last_name"], self.user.last_name)

        response = self.client.get(f"{self.list_url}?current=1", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.user.id))

    def test_list_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        response = self.client.get(self.list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        response = self.client.get(f"{self.list_url}?current=1", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.admin.id))

    def test_get_anonymouse(self):
        response = self.client.get(self.user_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(self.admin_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token.key}")

        response = self.client.get(self.user_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.user.id))
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["first_name"], self.user.first_name)
        self.assertEqual(response.data["last_name"], self.user.last_name)

        response = self.client.get(self.admin_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        response = self.client.get(self.user_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.user.id))

        response = self.client.get(self.admin_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.admin.id))

    def test_create_user(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.list_url, self.post_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(id=response.data["id"])
        self.assertTrue(user.check_password(self.post_data["password"]))
        self.assertFalse(user.is_active)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Welcome", mail.outbox[0].subject)
        match = re.search(
            r"(?P<url>https?://.*\?token=(?P<token>.*))$", mail.outbox[0].body
        )
        token = unquote(match.group("token"))
        self.assertIn("/register/activate?", match.group("url"))

        response = self.client.post(
            self.activate_account_url, {"token": token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_expired_activation_token(self):
        self.user.is_active = False
        self.user.save()

        mocked_time = Mock()
        expires_seconds = drf_user_settings.ACTIVATION_TOKEN_EXPIRES_SECONDS
        mocked_time.return_value = time.time() - expires_seconds.total_seconds()
        with patch("django.core.signing.time.time", mocked_time):
            token = generate_activation_token(self.user)

        response = self.client.post(
            self.activate_account_url,
            {"token": token},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_required_fields(self):
        post_data = self.post_data.copy()
        post_data.pop("first_name")
        response = self.client.post(
            self.list_url,
            post_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["first_name"][0], "This field is required.")

        post_data = self.post_data.copy()
        post_data.pop("last_name")
        response = self.client.post(
            self.list_url,
            post_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["last_name"][0], "This field is required.")

        post_data = self.post_data.copy()
        post_data.pop("email")
        response = self.client.post(
            self.list_url,
            post_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "This field is required.")

        post_data = self.post_data.copy()
        post_data.pop("password")
        response = self.client.post(
            self.list_url,
            post_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["password"][0], "This field is required.")


class ChangePasswordTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ADMIN_EMAIL = "admin@example.com"
        cls.ADMIN_PASSWORD = "p4ssWord123"
        cls.admin = User.objects.create_superuser(
            email=cls.ADMIN_EMAIL, password=cls.ADMIN_PASSWORD
        )
        cls.admin_token = Token.objects.create_token(user=cls.admin)

        cls.USER_EMAIL = "user@example.com"
        cls.USER_PASSWORD = "pa55word!"
        cls.user = User.objects.create_user(
            email=cls.USER_EMAIL, password=cls.USER_PASSWORD, is_active=True
        )
        cls.user_token = Token.objects.create_token(user=cls.user)

        cls.change_user_password_url = reverse(
            "user-change-password", kwargs={"id": cls.user.id}
        )
        cls.change_admin_password_url = reverse(
            "user-change-password", kwargs={"id": cls.admin.id}
        )

    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token.key}")

    def test_reset_password(self):
        new_password = "n3wp4ss!"

        response = self.client.post(
            self.change_user_password_url,
            {"current_password": self.USER_PASSWORD, "new_password": new_password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_reset_password_missing_current(self):
        response = self.client.post(
            self.change_user_password_url,
            {"new_password": "n3wp4ss!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["current_password"][0], "This field is required."
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.USER_PASSWORD))

    def test_reset_password_wrong_current(self):
        response = self.client.post(
            self.change_user_password_url,
            {"current_password": "wrong_password", "new_password": "n3wp4ss!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["current_password"][0], "Incorrect current password."
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.USER_PASSWORD))

    def test_reset_password_easy(self):
        response = self.client.post(
            self.change_user_password_url,
            {"current_password": self.USER_PASSWORD, "new_password": "n3wp4ss"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This password is too short.", response.data["new_password"][0])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.USER_PASSWORD))

    def test_reset_password_wrong_user(self):
        response = self.client.post(
            self.change_admin_password_url,
            {"current_password": self.ADMIN_PASSWORD, "new_password": "n3wp4ss!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password(self.ADMIN_PASSWORD))


class ResetPasswordTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_EMAIL = "user@example.com"
        cls.USER_PASSWORD = "pa55word!"
        cls.user = User.objects.create_user(
            email=cls.USER_EMAIL, password=cls.USER_PASSWORD, is_active=True
        )

        cls.request_reset_password_url = reverse("user-request-password-reset")
        cls.reset_password_url = reverse("user-password-reset")

    def test_reset_password(self):
        new_password = "n3wp4ss!"

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                self.request_reset_password_url,
                {"email": self.USER_EMAIL},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("password reset", mail.outbox[0].subject)
        match = re.search(
            r"(?P<url>https?://.*\?token=(?P<token>.*))$", mail.outbox[0].body
        )
        token = unquote(match.group("token"))
        self.assertIn("/password-reset?", match.group("url"))

        response = self.client.post(
            self.reset_password_url,
            {"token": token, "new_password": new_password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_expired_token(self):
        mocked_time = Mock()
        mocked_time.return_value = (
            time.time() - drf_user_settings.RESET_TOKEN_EXPIRES_SECONDS.total_seconds()
        )
        with patch("django.core.signing.time.time", mocked_time):
            token = generate_reset_token(self.user)

        response = self.client.post(
            self.reset_password_url,
            {"token": token, "new_password": "n3wp4ss!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "Bad token.")

    def test_old_counter(self):
        token = generate_reset_token(self.user)

        self.user.password_reset_counter = F("password_reset_counter") + 1
        self.user.save()

        response = self.client.post(
            self.reset_password_url,
            {"token": token, "new_password": "n3wp4ss!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "Bad token.")

    def test_inactive_user(self):
        token = generate_reset_token(self.user)

        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.reset_password_url,
            {"token": token, "new_password": "n3wp4ss!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Account is not activated", response.data["non_field_errors"][0])
