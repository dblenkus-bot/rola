"""Exercise the real host's contest notification and result integration."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from drf_user.models import Email, Location
from rola_integration.models import ContestNotification
from rolca.core.models import Author, Submission, SubmissionSet
from rolca.rating.models import (
    AuthorReward,
    Judge,
    Rating,
    SubmissionReward,
    ThemeResults,
)
from tests.test_workflows import payload, submitted
from tests.test_workflows import world as world

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("batch", [False, True])
def test_host_confirmation_is_sent_once_after_commit(
    world, batch, mailoutbox, django_capture_on_commit_callbacks
):
    template = Email.objects.create(subject="Thank you", body="Submitted")
    ContestNotification.objects.create(
        contest=world.contest, confirmation_email=template
    )
    data = payload(world)
    if batch:
        data = [data, payload(world)]
    with django_capture_on_commit_callbacks(execute=True):
        response = world.client.post("/api/v1/submission", data, format="json")
        assert not mailoutbox
    assert response.status_code == 201, response.data
    assert SubmissionSet.objects.get().user == world.owner
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [world.owner.email]


def test_rejected_submission_does_not_send_confirmation(
    world, mailoutbox, django_capture_on_commit_callbacks
):
    ContestNotification.objects.create(
        contest=world.contest,
        confirmation_email=Email.objects.create(subject="Thank you", body="Submitted"),
    )
    with django_capture_on_commit_callbacks(execute=True):
        response = world.client.post(
            "/api/v1/submission", payload(world, files=[{"id": 999999}]), format="json"
        )
    assert response.status_code == 400
    assert not mailoutbox
    assert not Submission.objects.exists()


def test_published_results_preload_host_country(world, django_assert_max_num_queries):
    world.owner.location = Location.objects.create(
        country="Slovenia", city="Ljubljana", address="", postal_code=""
    )
    world.owner.save()
    judge = Judge.objects.create(judge=world.other, contest=world.contest)
    ThemeResults.objects.create(theme=world.theme, accepted_threshold=3)
    for index in range(4):
        author = Author.objects.create(user=world.owner, first_name=f"Author {index}")
        if index == 0:
            AuthorReward.objects.create(
                author=author, theme=world.theme, label="Best author"
            )
        submission = submitted(world, author=author)
        Rating.objects.create(judge=judge, submission=submission, rating=5)
        SubmissionReward.objects.create(submission=submission, kind=1, label="Gold")
    world.contest.publish_date = timezone.now() - timedelta(seconds=1)
    world.contest.save()
    with django_assert_max_num_queries(4):
        response = APIClient().get("/api/v1/results/submission")
    assert response.status_code == 200, response.data
    assert [row["author"]["country"] for row in response.data["results"]] == [
        "Slovenia"
    ] * 4
    response = APIClient().get(f"/api/v1/results/theme/{world.theme.pk}")
    assert response.status_code == 200, response.data
    assert all(
        row["author"]["country"] == "Slovenia" for row in response.data["submissions"]
    )


def test_historical_thumbnail_migration_handles_existing_media(world):
    import importlib

    from django.db import connection
    from django.db.migrations.loader import MigrationLoader
    from django.test import override_settings
    from PIL import Image

    from rola_integration.migration_settings import LEGACY_MIGRATION_MODULES
    from tests.test_workflows import photo

    image = photo(world.owner)
    with override_settings(MIGRATION_MODULES=LEGACY_MIGRATION_MODULES):
        state = MigrationLoader(connection).project_state(
            [("core", "0016_submissionset_update_3")]
        )
    migration = importlib.import_module(
        "rola_integration.legacy_migrations.core.0017_enlarge_thumbnails"
    )
    migration.enlarge_thumbnails(state.apps, None)
    image.refresh_from_db()
    with image.thumbnail.open("rb") as source, Image.open(source) as thumbnail:
        assert thumbnail.size == (400, 300)
        assert thumbnail.format == "JPEG"
