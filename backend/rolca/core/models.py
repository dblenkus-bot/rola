""".. Ignore pydocstyle D400.

===========
Core models
===========

.. autoclass:: rolca.core.models.Contest
    :members:

.. autoclass:: rolca.core.models.Theme
    :members:

.. autoclass:: rolca.core.models.Author
    :members:

.. autoclass:: rolca.core.models.Submission
    :members:

.. autoclass:: rolca.core.models.File
    :members:

"""

import hashlib
import io
import os
import struct
import time

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image


class BaseModel(models.Model):
    """Base model for all other models."""

    class Meta:
        """BaseModel Meta options."""

        abstract = True

    #: user who created the object
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE
    )

    #: date when the object was created
    created = models.DateTimeField(auto_now_add=True)

    #: date when the object was last modified
    modified = models.DateTimeField(auto_now=True)


class Contest(BaseModel):
    """Model for storing contests.

    Contest object is the main object of single contest. It can contain
    multiple themes and all important dates for contest (start, end and
    results date).
    """

    class Meta:
        """Contest Meta options."""

        ordering = ["id"]
        verbose_name = _("contest")
        verbose_name_plural = _("contests")

    #: title of the contest
    title = models.CharField(_("Title"), max_length=100)

    #: description of the contest
    description = models.TextField(_("Description"), null=True, blank=True)

    #: date when contest starts
    start_date = models.DateTimeField(_("Start date"))

    #: date when contest ends
    end_date = models.DateTimeField(_("End date"))

    #: date when results will be published
    publish_date = models.DateTimeField(_("Publish date"), blank=True)

    #: indicate if user must be logged-in to participate in contest
    login_required = models.BooleanField(_("Login required"), default=False)

    #: header image of the contest
    header_image = models.ImageField(null=True, blank=True)

    #: notice in HTML form
    notice_html = models.TextField(default="")

    #: confirmation in HTML form
    confirmation_html = models.TextField(default="")

    dob_required = models.BooleanField(default=False)

    club_show = models.BooleanField(default=False)

    club_required = models.BooleanField(default=False)

    school_show = models.BooleanField(default=False)

    school_required = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """Save Contest instance."""
        if not self.publish_date:
            self.publish_date = self.end_date

        super().save(*args, **kwargs)

    def __str__(self):
        """Return Contest's title."""
        return self.title

    def is_active(self):
        """Check if contest is active."""
        return self.start_date <= timezone.now() <= self.end_date

    is_active.admin_order_field = "end_date"
    is_active.boolean = True
    is_active.short_description = _("active")

    def number_of_photos(self):
        """Return number of photos submitted to the current contest."""
        return Submission.objects.filter(theme__contest=self).count()

    number_of_photos.short_description = _("number of submissons")


class Theme(BaseModel):
    """Model for storing themes."""

    class Meta:
        """Theme Meta options."""

        ordering = ["id"]
        verbose_name = _("theme")
        verbose_name_plural = _("themes")

    #: title of the theme
    title = models.CharField(_("Title"), max_length=100)

    #: contest that theme belongs to
    contest = models.ForeignKey(
        Contest, related_name="themes", on_delete=models.CASCADE
    )

    #: indicates whether the theme is a series or not
    is_series = models.BooleanField(default=False)

    #: number of photos that can be submited to theme
    n_photos = models.IntegerField(_("Number of photos"))

    def save(self, *args, **kwargs):
        """Save Theme instance."""
        if getattr(self, "user", None) is None:
            self.user = self.contest.user

        super().save(*args, **kwargs)

    def __str__(self):
        """Return theme's title."""
        return self.title


def _generate_filename(instance, filename, prefix):
    """Generate unique filename with given prefix."""
    md5 = hashlib.md5()
    md5.update(struct.pack("f", time.time()))
    was_closed = instance.file.closed
    try:
        if was_closed:
            instance.file.open("rb")
        for chunk in instance.file.chunks():
            md5.update(chunk)
    finally:
        if was_closed:
            instance.file.close()
    extension = os.path.splitext(filename)[1]
    return os.path.join(prefix, md5.hexdigest() + extension)


def generate_file_filename(instance, filename):
    """Generate filename for uploaded photo."""
    return _generate_filename(instance, filename, "photos")


def generate_thumb_filename(instance, filename):
    """Generate filename for thumbnails of uploaded photos."""
    return _generate_filename(instance, filename, "thumbs")


class SubmissionSet(BaseModel):
    """Model for organizing submissions."""

    class Meta:
        """SubmissionSet Meta options."""

        ordering = ["id"]
        verbose_name = _("submission set")
        verbose_name_plural = _("submission sets")

    submissions = models.ManyToManyField("Submission")

    contest = models.ForeignKey(
        Contest, on_delete=models.CASCADE, related_name="submission_sets"
    )

    author = models.ForeignKey("Author", on_delete=models.CASCADE)

    def __str__(self):
        """Return string representation of SubmissionSet object."""

        first_submission = self.submissions.first()
        author = first_submission.author if first_submission else "/"
        return f"{self.submissions.count()} submissions by {author}"


class Submission(BaseModel):
    """Model for storing uploaded submissions."""

    class Meta:
        """Submission Meta options."""

        ordering = ["id"]
        verbose_name = _("submission")
        verbose_name_plural = _("submissions")

    title = models.CharField(_("Title"), max_length=100, null=True, blank=True)

    description = models.TextField(null=True, blank=True)

    author = models.ForeignKey("Author", on_delete=models.CASCADE)

    theme = models.ForeignKey(Theme, on_delete=models.PROTECT)

    def __str__(self):
        """Return string representation of Submission object."""
        return self.title


def validate_image(file):
    """Validate the upload size and longest image edge."""
    max_size = settings.ROLCA_MAX_UPLOAD_SIZE
    if file.size > max_size:
        raise ValidationError(f"Max size of file is {max_size}B.")

    max_res = settings.ROLCA_MAX_UPLOAD_RESOLUTION
    if max(file.image.size) > max_res:
        raise ValidationError(f"Max photo resolution is {max_res}px.")


class File(BaseModel):
    """Model for storing uploaded images.

    Uploaded images can be stored prior to creating Submission
    instance. This way you can upload images while user is typing other
    data.Images are checked if meet size and format requirements before
    saving.

    """

    class Meta:
        """File Meta options."""

        ordering = ["id"]
        verbose_name = _("file")
        verbose_name_plural = _("files")

    submission = models.ForeignKey(
        Submission, related_name="files", null=True, on_delete=models.CASCADE
    )

    #: uploaded file
    file = models.ImageField(
        upload_to=generate_file_filename, validators=[validate_image]
    )

    #: thumbnail of uploaded file
    thumbnail = models.ImageField(upload_to=generate_thumb_filename)

    def save(self, *args, **kwargs):
        """Add photo thumbnail and save object."""
        if not self.pk:  # on create
            thumb = io.BytesIO()
            with Image.open(self.file) as image:
                image.thumbnail((400, 400), Image.Resampling.LANCZOS)
                image.save(
                    thumb, format="jpeg", quality=80, optimize=True, progressive=True
                )
            self.thumbnail = InMemoryUploadedFile(
                thumb, None, self.file.name, "image/jpeg", thumb.tell(), None
            )

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete attached images and actual object."""
        self.file.delete(save=False)
        self.thumbnail.delete(save=False)

        super().delete(*args, **kwargs)

    def get_long_edge(self):
        """Return longer edge of the image."""
        return max(self.file.width, self.file.height)

    def __str__(self):
        """Return string representation of File object."""
        submission_title = self.submission.title if self.submission else "?"
        submission_id = self.submission.pk if self.submission else "?"
        return f"id: {self.pk}, filename: {self.file.name}, submission id: {submission_id}, submission title: {submission_title}"


class Institution(BaseModel):
    """Store a participating institution."""

    SCHOOL = 1
    KIND_CHOICES = [
        (SCHOOL, "School"),
    ]

    kind = models.SmallIntegerField(choices=KIND_CHOICES)

    name = models.CharField(max_length=100)

    class Meta:
        """Keep institution names unique within each kind."""

        constraints = [
            models.UniqueConstraint(fields=["kind", "name"], name="unique_name_kind"),
        ]


class Author(BaseModel):
    """Model for storing participents."""

    class Meta:
        """Author Meta options."""

        ordering = ["id"]
        verbose_name = _("author")
        verbose_name_plural = _("authors")

    #: ``Author``'s first name
    first_name = models.CharField(_("First name"), max_length=30)

    #: ``Author``'s last name
    last_name = models.CharField(_("Last name"), max_length=30)

    #: ``Author``'s email
    email = models.EmailField(_("Email"), null=True, blank=True)

    dob = models.DateField(null=True, blank=True)

    school = models.CharField(max_length=100, null=True, blank=True)

    mentor = models.CharField(max_length=100, null=True, blank=True)

    club = models.CharField(max_length=100, null=True, blank=True)

    distinction = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        """Return string representation of Author object."""
        return f"{self.first_name} {self.last_name}"
