""".. Ignore pydocstyle D400.

======================
Rating API serializers
======================

.. autoclass:: rolca.rating.api.serializers.RatingSerializer
    :members:

"""

from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import exceptions, serializers

from rolca.core.api.serializers import AuthorSerializer as CoreAuthorSerializer
from rolca.core.api.serializers import BaseSerializer, FileSerializer
from rolca.core.api.serializers import ContestSerializer as CoreContestSerializer
from rolca.core.api.serializers import SubmissionSerializer as CoreSubmissionSerializer
from rolca.core.api.serializers import ThemeSerializer as CoreThemeSerializer
from rolca.integration import get_author_country
from rolca.rating.models import Judge, Rating, SubmissionReward


class RatingSerializer(BaseSerializer):
    """Serializer for Rating objects."""

    class Meta(BaseSerializer.Meta):
        """Serializer configuration."""

        model = Rating
        fields = BaseSerializer.Meta.fields + ["submission", "rating"]

    def create(self, validated_data):
        """Create or replace the requesting judge's score."""
        submission = validated_data.pop("submission")
        try:
            user = self.context["request"].user
            judge = Judge.objects.get(judge=user, contest=submission.theme.contest)
        except Judge.DoesNotExist:
            raise exceptions.NotAuthenticated(
                "You don't have permission to rate this contest."
            ) from None

        rating, _ = Rating.objects.update_or_create(
            submission=submission, judge=judge, defaults=validated_data
        )

        return rating

    def validate(self, attrs):
        """Keep a rating tied to its original submission and active judge."""
        submission = attrs.get(
            "submission", self.instance.submission if self.instance else None
        )
        if self.instance and submission.pk != self.instance.submission_id:
            raise serializers.ValidationError(
                {"submission": "The submission cannot be changed."}
            )
        if (
            submission
            and not Judge.objects.filter(
                judge=self.context["request"].user,
                contest=submission.theme.contest,
                contest__publish_date__gt=timezone.now(),
            ).exists()
        ):
            raise serializers.ValidationError(
                "Only active judges can rate this contest."
            )
        return attrs


class JudgeThemeSerializer(CoreThemeSerializer):
    """Serializer for Theme objects."""

    ratings_number = serializers.SerializerMethodField("get_ratings_number")
    submissions_number = serializers.SerializerMethodField("get_submissions_number")

    class Meta(CoreThemeSerializer.Meta):
        """Serializer configuration."""

        fields = CoreThemeSerializer.Meta.fields + [
            "ratings_number",
        ]

    def get_ratings_number(self, theme) -> int:
        """Count ratings submitted by the requesting judge."""
        return Rating.objects.filter(
            user=self.context["request"].user, submission__theme=theme
        ).count()

    def get_submissions_number(self, theme) -> int:
        """Count paid submissions available for judging."""
        return theme.submission_set.filter(submissionset__payment__paid=True).count()


class JudgeContestSerializer(CoreContestSerializer):
    """Serializer for Contest objects."""

    themes = JudgeThemeSerializer(many=True, read_only=True)


class AuthorResultsSerializer(CoreAuthorSerializer):
    """Serializer for Theme objects."""

    reward = serializers.CharField(
        source="reward.label", read_only=True, allow_null=True, default=None
    )
    reward_theme = serializers.IntegerField(
        source="reward.theme_id", read_only=True, allow_null=True, default=None
    )
    country = serializers.SerializerMethodField("get_country")

    class Meta(CoreAuthorSerializer.Meta):
        """Serializer configuration."""

        fields = CoreAuthorSerializer.Meta.fields + [
            "reward",
            "reward_theme",
            "country",
        ]

    def get_country(self, author) -> str | None:
        """Return the optional country supplied by the host user model."""
        return get_author_country(author)


class SubmissionResultsSerializer(CoreSubmissionSerializer):
    """Serialize published submission results and awards."""

    accepted = serializers.SerializerMethodField("get_accepted")
    reward_kind = serializers.SerializerMethodField("get_reward_kind")
    reward_label = serializers.CharField(
        source="reward.label", read_only=True, allow_null=True, default=None
    )
    rating = serializers.IntegerField(
        source="rating_sum", read_only=True, allow_null=True
    )

    class Meta(CoreSubmissionSerializer.Meta):
        """Serializer configuration."""

        fields = CoreSubmissionSerializer.Meta.fields + [
            "accepted",
            "rating",
            "reward_kind",
            "reward_label",
        ]

    def get_fields(self):
        """Include result-specific author and file representations."""
        fields = super().get_fields()
        fields["files"] = serializers.SerializerMethodField("get_files")
        fields["author"] = AuthorResultsSerializer()

        return fields

    def _is_accepted(self, submission):
        if submission.rating_sum is None:
            return False

        if "accept_threshold" in self.context:
            return submission.rating_sum >= self.context["accept_threshold"]

        return submission.rating_sum >= submission.theme.results.accepted_threshold

    def get_accepted(self, submission) -> bool:
        """Report whether the submission reached the acceptance threshold."""
        return self._is_accepted(submission)

    @extend_schema_field(FileSerializer(many=True, allow_null=True))
    def get_files(self, submission):
        """Expose files only for accepted submissions."""
        if not self._is_accepted(submission):
            return None

        return FileSerializer(
            submission.files,
            many=True,
            context={
                "request": self.context["request"],
            },
        ).data

    def get_reward_kind(self, submission) -> str | None:
        """Return the human-readable award kind when present."""
        mapping = dict(SubmissionReward.KIND_CHOICES)
        if hasattr(submission, "reward"):
            return mapping[submission.reward.kind]


class ThemeResultsSerializer(CoreThemeSerializer):
    """Serializer for Theme results."""

    submissions = serializers.SerializerMethodField("get_submissions")

    class Meta(CoreThemeSerializer.Meta):
        """Serializer configuration."""

        fields = CoreThemeSerializer.Meta.fields + [
            "submissions",
        ]

    @extend_schema_field(SubmissionResultsSerializer(many=True))
    def get_submissions(self, theme):
        """Serialize each submission against the theme acceptance threshold."""
        return SubmissionResultsSerializer(
            theme.submission_set.all(),
            many=True,
            context={
                "request": self.context["request"],
                "accept_threshold": theme.results.accepted_threshold,
            },
        ).data
