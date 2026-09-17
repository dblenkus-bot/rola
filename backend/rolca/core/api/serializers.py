""".. Ignore pydocstyle D400.

====================
Core API serializers
====================

.. autoclass:: rolca.core.api.serializers.FileSerializer
    :members:

.. autoclass:: rolca.core.api.serializers.SubmissionSerializer
    :members:

.. autoclass:: rolca.core.api.serializers.ThemeSerializer
    :members:

.. autoclass:: rolca.core.api.serializers.ContestSerializer
    :members:

"""

from rest_framework import serializers

from rolca.core.models import (
    Author,
    Contest,
    File,
    Institution,
    Submission,
    SubmissionSet,
    Theme,
)


class BaseSerializer(serializers.ModelSerializer):
    """Base serializer for Rolca models."""

    user = serializers.HiddenField(
        default=serializers.CreateOnlyDefault(serializers.CurrentUserDefault())
    )

    class Meta:
        """Serializer configuration."""

        fields = ["id", "user", "created", "modified"]
        read_only_fields = ["id"]


class IdRelatedSerializer(serializers.Serializer):
    """Serializer for File objects."""

    id = serializers.IntegerField()


class FileSerializer(BaseSerializer):
    """Serializer for File objects."""

    class Meta(BaseSerializer.Meta):
        """Serializer configuration."""

        model = File
        fields = BaseSerializer.Meta.fields + ["file", "thumbnail"]
        extra_kwargs = {
            "thumbnail": {"required": False},
        }


class InstitutionSerializer(BaseSerializer):
    """Serializer for Author objects."""

    class Meta(BaseSerializer.Meta):
        """Serializer configuration."""

        model = Institution
        fields = BaseSerializer.Meta.fields + ["name", "kind"]


class AuthorSerializer(BaseSerializer):
    """Serializer for Author objects."""

    email = serializers.SerializerMethodField("get_email")

    class Meta(BaseSerializer.Meta):
        """Serializer configuration."""

        model = Author
        fields = BaseSerializer.Meta.fields + [
            "first_name",
            "last_name",
            "email",
            "dob",
            "school",
            "mentor",
            "club",
            "distinction",
        ]

    def get_email(self, author) -> str | None:
        """Return author's email for superusers, ``None`` field otherwise."""
        if not self.context["request"].user.is_superuser:
            return None

        if author.user is None:
            return author.email
        email_field = author.user.get_email_field_name()
        return getattr(author.user, email_field, None)


class SubmissionSerializer(BaseSerializer):
    """Serializer for Submission objects."""

    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all())

    class Meta(BaseSerializer.Meta):
        """Serializer configuration."""

        model = Submission
        fields = BaseSerializer.Meta.fields + [
            "author",
            "theme",
            "title",
            "description",
            "files",
        ]

    def get_fields(self):
        """Dynamically adapt fields based on the current request."""
        fields = super().get_fields()

        if self.context["request"].method == "GET":
            fields["author"] = AuthorSerializer()
            fields["files"] = FileSerializer(many=True)
        else:
            fields["author"] = IdRelatedSerializer()
            fields["files"] = IdRelatedSerializer(many=True)

        return fields

    def validate_files(self, value):
        """Reject missing, foreign, duplicate, or already attached uploads."""
        file_ids = [file["id"] for file in value]
        if len(file_ids) != len(set(file_ids)):
            raise serializers.ValidationError("Each file may only be used once.")
        files = list(
            File.objects.filter(id__in=file_ids, user=self.context["request"].user)
        )
        if len(files) != len(file_ids):
            raise serializers.ValidationError("Files must exist and belong to you.")
        allowed_submission = self.instance.pk if self.instance else None
        if any(file.submission_id not in (None, allowed_submission) for file in files):
            raise serializers.ValidationError(
                "A file is already attached to another submission."
            )
        return files

    def validate_author(self, value):
        """Resolve only authors owned by the current user."""
        try:
            return Author.objects.get(pk=value["id"], user=self.context["request"].user)
        except Author.DoesNotExist as error:
            raise serializers.ValidationError(
                "Author must exist and belong to you."
            ) from error

    def validate(self, attrs):
        """Keep existing submission groups consistent when editing."""
        if self.instance:
            if "author" in attrs and attrs["author"].pk != self.instance.author_id:
                raise serializers.ValidationError(
                    {"author": "The author cannot be changed."}
                )
            if (
                "theme" in attrs
                and attrs["theme"].contest_id != self.instance.theme.contest_id
            ):
                raise serializers.ValidationError(
                    {"theme": "The contest cannot be changed."}
                )
        return attrs

    def create(self, validated_data):
        """Create a submission and attach its validated uploads."""
        files = validated_data.pop("files")
        submission = Submission.objects.create(**validated_data)
        submission.files.add(*files)
        return submission

    def update(self, instance, validated_data):
        """Replace uploaded-file relations only when supplied by the client."""
        files = validated_data.pop("files", None)
        instance = super().update(instance, validated_data)
        if files is not None:
            instance.files.set(files)
        return instance


class SubmissionSetSerializer(BaseSerializer):
    """Serializer for SubmissionSet objects."""

    submissions = SubmissionSerializer(many=True)

    class Meta(BaseSerializer.Meta):
        """Serializer configuration."""

        model = SubmissionSet
        fields = BaseSerializer.Meta.fields + ["submissions", "author", "contest"]

    def get_fields(self):
        """Dynamically adapt fields based on the current request."""
        fields = super().get_fields()

        if self.context["request"].method == "GET":
            fields["author"] = AuthorSerializer()
        else:
            fields["author"] = IdRelatedSerializer()

        return fields


class ThemeSerializer(BaseSerializer):
    """Serializer for Theme objects."""

    submissions_number = serializers.SerializerMethodField("get_submissions_number")

    class Meta(BaseSerializer.Meta):
        """Serializer configuration."""

        model = Theme
        fields = BaseSerializer.Meta.fields + [
            "title",
            "is_series",
            "n_photos",
            "submissions_number",
        ]

    def get_submissions_number(self, theme) -> int:
        """Count submissions in this theme."""
        return theme.submission_set.count()


class ContestSerializer(BaseSerializer):
    """Serializer for Contest objects."""

    themes = ThemeSerializer(many=True, read_only=True)

    class Meta(BaseSerializer.Meta):
        """Serializer configuration."""

        model = Contest
        fields = BaseSerializer.Meta.fields + [
            "title",
            "description",
            "start_date",
            "end_date",
            "themes",
            "header_image",
            "notice_html",
            "confirmation_html",
            "dob_required",
            "club_show",
            "club_required",
            "school_show",
            "school_required",
        ]
