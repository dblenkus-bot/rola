""".. Ignore pydocstyle D400."""

from django.db.models import CharField, F, Prefetch, Sum, Value
from django.db.models.functions import SHA1, Cast, Concat
from django.utils import timezone
from rest_framework import mixins, permissions, viewsets

from rolca.core.api.filters import ContestFilter, SubmissionFilter
from rolca.core.api.serializers import SubmissionSerializer
from rolca.core.models import Contest, Submission, Theme
from rolca.integration import author_select_related
from rolca.rating.api.filters import RatingFilter
from rolca.rating.api.permissions import CanModifyRating, IsActiveJudge
from rolca.rating.api.serializers import (
    ContestSerializer,
    RatingSerializer,
    SubmissionResultsSerializer,
    ThemeResultsSerializer,
)
from rolca.rating.models import Judge, Rating


class RatingViewSet(viewsets.ModelViewSet):
    """API viewset for Rating objects."""

    queryset = Rating.objects.none()
    serializer_class = RatingSerializer
    permission_classes = (permissions.IsAuthenticated, CanModifyRating)
    filterset_class = RatingFilter

    def get_queryset(self):
        """Restrict ratings to the requesting user."""
        return Rating.objects.filter(user=self.request.user)


class SubmissionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """List paid submissions assigned to an active judge."""

    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    filterset_class = SubmissionFilter
    permission_classes = (IsActiveJudge,)

    def get_queryset(self):
        """Return queryset for submissions that can be shown to judge."""
        judge_qs = Judge.objects.filter(judge=self.request.user)
        theme_qs = Theme.objects.filter(
            contest__in=judge_qs.values("contest"),
            contest__publish_date__gte=timezone.now(),
        )
        return (
            Submission.objects.filter(
                theme__in=theme_qs,
                submissionset__payment__paid=True,
            )
            .annotate(
                random=SHA1(
                    Concat(Cast("pk", CharField()), Value(str(self.request.user.pk)))
                )
            )
            .order_by("random")
        )


class ContestViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """List contests assigned to the requesting judge."""

    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    filterset_class = ContestFilter
    permission_classes = (IsActiveJudge,)

    def get_queryset(self):
        """Return queryset for contests that can be shown to judge."""
        judge_qs = Judge.objects.filter(judge=self.request.user)
        return Contest.objects.filter(
            pk__in=judge_qs.values("contest"),
            publish_date__gte=timezone.now(),
        )


def _result_submissions():
    """Preload result fields and the host's optional author relationships."""
    return (
        Submission.objects.annotate(rating_sum=Sum("rating__rating"))
        .select_related(
            "theme__results", "author__reward", *author_select_related("author")
        )
        .prefetch_related("files", "reward")
    )


class ThemeResultsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Retrieve published results for a theme."""

    queryset = Theme.objects.none()
    serializer_class = ThemeResultsSerializer

    def get_queryset(self):
        """Load published themes and their submissions with host author fields."""
        return (
            Theme.objects.filter(contest__publish_date__lte=timezone.now())
            .select_related("results")
            .prefetch_related(
                Prefetch("submission_set", queryset=_result_submissions())
            )
        )


class SubmissionResultsViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """List and retrieve accepted submissions after publication."""

    queryset = Submission.objects.none()
    serializer_class = SubmissionResultsSerializer
    filterset_class = SubmissionFilter
    ordering_fields = ["rating_sum"]

    def get_queryset(self):
        """Return accepted published submissions with host author fields."""
        return _result_submissions().filter(
            rating_sum__gte=F("theme__results__accepted_threshold"),
            theme__contest__publish_date__lte=timezone.now(),
        )
