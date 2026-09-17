""".. Ignore pydocstyle D400.

==============
Core API views
==============

.. autoclass:: rolca.core.api.views.FileViewSet
    :members:

.. autoclass:: rolca.core.api.views.ContestViewSet
    :members:

"""

import logging

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import exceptions, mixins, permissions, status, viewsets
from rest_framework.response import Response

from rolca.core.api.filters import (
    ContestFilter,
    InstitutionFilter,
    SubmissionFilter,
    SubmissionSetFilter,
)
from rolca.core.api.parsers import ImageUploadParser
from rolca.core.api.permissions import AdminOrReadOnly, IsSubmissionOwnerOrReadOnly
from rolca.core.api.serializers import (
    AuthorSerializer,
    ContestSerializer,
    FileSerializer,
    InstitutionSerializer,
    SubmissionSerializer,
    SubmissionSetSerializer,
)
from rolca.core.models import (
    Author,
    Contest,
    File,
    Institution,
    Submission,
    SubmissionSet,
)
from rolca.integration import schedule_submission_confirmation

logger = logging.getLogger(__name__)


class FileViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """API viewset for File objects."""

    parser_classes = [ImageUploadParser]
    serializer_class = FileSerializer
    queryset = File.objects.none()
    permission_classes = (permissions.IsAuthenticated,)


class InstitutionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """List institutions with optional filters."""

    queryset = Institution.objects.order_by("pk")
    serializer_class = InstitutionSerializer
    filterset_class = InstitutionFilter


class AuthorViewSet(viewsets.ModelViewSet):
    """API viewset for Author objects."""

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """Restrict authors to their owner unless the requester is an administrator."""
        queryset = self.queryset
        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(user=self.request.user)


class SubmissionViewSet(viewsets.ModelViewSet):
    """API view Submission objects."""

    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsSubmissionOwnerOrReadOnly)
    filterset_class = SubmissionFilter

    def get_queryset(self):
        """Return queryset for submissions that can be shown to user.

        Return:
        * all submissions for already finished contests
        * user's submissions

        """
        return Submission.objects.filter(
            Q(user=self.request.user)
            | Q(theme__contest__publish_date__lte=timezone.now())
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create one coherent submission set, atomically, for either payload shape."""
        serializer_kwargs = {}
        if isinstance(request.data, list):
            serializer_kwargs.update(many=True, allow_empty=False)

        serializer = self.get_serializer(data=request.data, **serializer_kwargs)
        serializer.is_valid(raise_exception=True)
        items = (
            serializer.validated_data
            if serializer_kwargs
            else [serializer.validated_data]
        )
        contest = items[0]["theme"].contest
        if any(item["theme"].contest_id != contest.pk for item in items):
            raise exceptions.ValidationError(
                "All submissions must belong to the same contest."
            )
        if any(item["author"] != items[0]["author"] for item in items):
            raise exceptions.ValidationError(
                "All submissions must have the same author."
            )
        files = [file for item in items for file in item["files"]]
        if len({file.pk for file in files}) != len(files):
            raise exceptions.ValidationError(
                "Each file may only be used once in a submission set."
            )
        self._lock_files(files)
        self.perform_create(serializer)

        instances = serializer.instance if serializer_kwargs else [serializer.instance]
        first_instance = instances[0]

        submission_set = SubmissionSet.objects.create(
            author=first_instance.author, user=first_instance.user, contest=contest
        )
        submission_set.submissions.add(*instances)

        schedule_submission_confirmation(submission_set)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def _lock_files(self, files, submission=None):
        """Recheck attachment state under a lock to prevent concurrent file reuse."""
        locked = list(
            File.objects.select_for_update()
            .filter(pk__in=[file.pk for file in files])
            .order_by("pk")
        )
        if len(locked) != len(files) or any(
            file.user_id != self.request.user.pk
            or file.submission_id not in (None, submission)
            for file in locked
        ):
            raise exceptions.ValidationError(
                {"files": "An upload is no longer available."}
            )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Serialize file reassignment with other submission writes."""
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """Lock uploads before changing their submission relation."""
        if "files" in serializer.validated_data:
            self._lock_files(serializer.validated_data["files"], serializer.instance.pk)
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Delete an unpublished submission owned by the requester."""
        instance = self.get_object()

        if request.user != instance.user:
            raise exceptions.PermissionDenied(
                "You can only delete your own submissions."
            )
        if instance.theme.contest.publish_date < timezone.now():
            raise exceptions.PermissionDenied(
                "You cannot delete already published submissions."
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubmissionSetViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """List and delete the requesting user's submission sets."""

    queryset = SubmissionSet.objects.all()
    serializer_class = SubmissionSetSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_class = SubmissionSetFilter

    def get_queryset(self):
        """Return queryset for submissions that can be shown to user.

        Return:
        * all submissions for already finished contests
        * user's submissions

        """
        if self.request.user.is_superuser:
            return self.queryset

        return self.queryset.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Destroy the instance and all related submissions."""
        instance = self.get_object()

        if instance.contest.publish_date < timezone.now():
            raise exceptions.PermissionDenied(
                "You cannot delete already published submission sets."
            )

        instance.submissions.all().delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContestViewSet(viewsets.ModelViewSet):
    """API view Contest objects."""

    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    permission_classes = (AdminOrReadOnly,)
    filterset_class = ContestFilter
