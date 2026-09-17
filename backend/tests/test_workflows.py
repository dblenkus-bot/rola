"""Regression tests for public APIs using the host's custom user contract."""

import io
import zipfile
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image
from rest_framework.test import APIClient

from rolca.core.models import (
    Author,
    Contest,
    File,
    Institution,
    Submission,
    SubmissionSet,
    Theme,
)
from rolca.payment.models import Payment
from rolca.rating.models import Judge, Rating, SubmissionReward, ThemeResults
from tests.factories import create_user

confirmation_callback = Mock()

pytestmark = pytest.mark.django_db


@pytest.fixture
def world():
    owner = create_user("owner")
    other = create_user("other")
    admin = create_user("admin", superuser=True)
    now = timezone.now()
    contest = Contest.objects.create(
        user=admin,
        title="Salon",
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=1),
        publish_date=now + timedelta(days=2),
    )
    theme = Theme.objects.create(contest=contest, title="Nature", n_photos=4)
    author = Author.objects.create(
        user=owner, first_name="Alice", last_name="Photographer"
    )
    other_author = Author.objects.create(user=other, first_name="Other")
    client = APIClient()
    client.force_authenticate(owner)
    return SimpleNamespace(
        owner=owner,
        other=other,
        admin=admin,
        contest=contest,
        theme=theme,
        author=author,
        other_author=other_author,
        client=client,
    )


def rows(response):
    """Read list responses with or without the host's pagination envelope."""
    return (
        response.data["results"] if isinstance(response.data, dict) else response.data
    )


def photo(user, name="photo.jpg"):
    data = io.BytesIO()
    Image.new("RGB", (800, 600), "red").save(data, "JPEG")
    return File.objects.create(
        user=user,
        file=SimpleUploadedFile(name, data.getvalue(), content_type="image/jpeg"),
    )


def payload(world, **changes):
    result = {
        "title": "Photo",
        "theme": world.theme.pk,
        "author": {"id": world.author.pk},
        "files": [{"id": photo(world.owner).pk}],
    }
    result.update(changes)
    return result


def submitted(world, **changes):
    data = dict(
        user=world.owner, title="Original", theme=world.theme, author=world.author
    )
    data.update(changes)
    return Submission.objects.create(**data)


def test_author_list_is_scoped_to_requesting_user(world):
    response = world.client.get("/api/author/")
    assert response.status_code == 200
    assert [item["id"] for item in rows(response)] == [world.author.pk]


@pytest.mark.parametrize("batch", [False, True])
def test_submission_creates_set_and_sends_one_confirmation_after_commit(
    world, batch, settings, django_capture_on_commit_callbacks
):
    settings.ROLCA_SUBMISSION_CONFIRMATION_CALLBACK = (
        "tests.test_workflows.confirmation_callback"
    )
    confirmation_callback.reset_mock()
    data = payload(world)
    if batch:
        data = [data, payload(world)]
    with django_capture_on_commit_callbacks(execute=True):
        response = world.client.post("/api/submission/", data, format="json")
        confirmation_callback.assert_not_called()
    assert response.status_code == 201, response.data
    assert isinstance(response.data, list) == batch
    group = SubmissionSet.objects.get()
    assert group.author == world.author
    assert group.contest == world.contest
    assert group.user == world.owner
    assert group.submissions.count() == (2 if batch else 1)
    confirmation_callback.assert_called_once_with(group)


@pytest.mark.parametrize(
    "case",
    [
        "empty",
        "unknown_author",
        "other_author",
        "unknown_file",
        "other_file",
        "duplicate_files",
        "attached_file",
        "mixed_contests",
        "mixed_authors",
        "reused_batch_file",
    ],
)
def test_invalid_submission_leaves_no_partial_records(world, case):
    data = payload(world)
    if case == "empty":
        data = []
    elif case == "unknown_author":
        data["author"] = {"id": 999999}
    elif case == "other_author":
        data["author"] = {"id": world.other_author.pk}
    elif case == "unknown_file":
        data["files"] = [{"id": 999999}]
    elif case == "other_file":
        data["files"] = [{"id": photo(world.other).pk}]
    elif case == "duplicate_files":
        data["files"] *= 2
    elif case == "attached_file":
        existing = submitted(world)
        File.objects.filter(pk=data["files"][0]["id"]).update(submission=existing)
    elif case == "mixed_contests":
        contest = Contest.objects.create(
            title="Second",
            start_date=world.contest.start_date,
            end_date=world.contest.end_date,
        )
        theme = Theme.objects.create(title="Second", contest=contest, n_photos=4)
        data = [data, payload(world, theme=theme.pk)]
    elif case == "mixed_authors":
        another = Author.objects.create(user=world.owner, first_name="Another")
        data = [data, payload(world, author={"id": another.pk})]
    elif case == "reused_batch_file":
        data = [data, dict(data)]
    before = Submission.objects.count()
    response = world.client.post("/api/submission/", data, format="json")
    assert response.status_code == 400, response.data
    assert Submission.objects.count() == before
    assert SubmissionSet.objects.count() == 0


def test_submission_database_failure_rolls_back_files_and_records(
    world, django_capture_on_commit_callbacks
):
    data = payload(world)
    with (
        django_capture_on_commit_callbacks(execute=True) as callbacks,
        patch(
            "rolca.core.api.views.SubmissionSet.objects.create",
            side_effect=RuntimeError("database failure"),
        ),
        pytest.raises(RuntimeError, match="database failure"),
    ):
        world.client.post("/api/submission/", data, format="json")
    assert not callbacks
    assert not Submission.objects.exists()
    assert File.objects.get(pk=data["files"][0]["id"]).submission_id is None


@pytest.mark.parametrize("method", ["put", "patch", "delete"])
def test_published_foreign_submission_cannot_be_modified(world, method):
    world.contest.publish_date = timezone.now() - timedelta(hours=1)
    world.contest.save()
    item = submitted(world, user=world.other, author=world.other_author)
    response = getattr(world.client, method)(
        f"/api/submission/{item.pk}/", {"title": "Changed"}, format="json"
    )
    assert response.status_code == 403
    item.refresh_from_db()
    assert item.title == "Original"
    assert item.user == world.other


def test_owner_can_patch_submission_and_replace_own_files(world):
    item = submitted(world)
    old = photo(world.owner)
    old.submission = item
    old.save()
    new = photo(world.owner)
    response = world.client.patch(
        f"/api/submission/{item.pk}/",
        {"title": "Edited", "files": [{"id": new.pk}]},
        format="json",
    )
    assert response.status_code == 200, response.data
    item.refresh_from_db()
    old.refresh_from_db()
    assert item.title == "Edited"
    assert item.user == world.owner
    assert list(item.files.values_list("pk", flat=True)) == [new.pk]
    assert old.submission_id is None


def test_submission_cannot_change_contest_or_author_after_grouping(world):
    response = world.client.post("/api/submission/", payload(world), format="json")
    assert response.status_code == 201
    author = Author.objects.create(user=world.owner, first_name="Another")
    response = world.client.patch(
        f"/api/submission/{response.data['id']}/",
        {"author": {"id": author.pk}},
        format="json",
    )
    assert response.status_code == 400


def test_owner_cannot_change_published_submission(world):
    item = submitted(world)
    world.contest.publish_date = timezone.now() - timedelta(seconds=1)
    world.contest.save()
    assert (
        world.client.patch(
            f"/api/submission/{item.pk}/", {"title": "Late"}, format="json"
        ).status_code
        == 403
    )


def test_contest_and_institution_filters_are_applied(world):
    Contest.objects.create(
        title="Past",
        start_date=timezone.now() - timedelta(days=4),
        end_date=timezone.now() - timedelta(days=2),
    )
    response = world.client.get("/api/contest/", {"is_active": "true"})
    assert [item["id"] for item in rows(response)] == [world.contest.pk]
    desired = Institution.objects.create(kind=1, name="School")
    Institution.objects.create(kind=1, name="Elsewhere")
    assert [
        item["id"]
        for item in rows(world.client.get("/api/institution/", {"name": "School"}))
    ] == [desired.pk]


def test_submission_and_set_filters_are_applied(world):
    item = submitted(world)
    group = SubmissionSet.objects.create(
        user=world.owner, author=world.author, contest=world.contest
    )
    group.submissions.add(item)
    assert rows(world.client.get("/api/submission/", {"contest": 999999})) == []
    other_contest = Contest.objects.create(
        title="Empty",
        start_date=world.contest.start_date,
        end_date=world.contest.end_date,
    )
    assert (
        rows(world.client.get("/api/submissionset/", {"contest": other_contest.pk}))
        == []
    )


def test_export_requires_organizer_and_includes_every_file(world):
    item = submitted(world)
    files = [photo(world.owner, "first.jpg"), photo(world.owner, "second.jpg")]
    item.files.add(*files)
    url = f"/core/contest/{world.contest.pk}/download"
    world.client.force_login(world.owner)
    assert world.client.get(url).status_code == 403
    world.client.force_login(world.admin)
    response = world.client.get(url)
    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        members = [name for name in archive.namelist() if not name.endswith("/")]
        assert len(members) == 2
        assert len(set(members)) == 2
        for name in members:
            assert Image.open(io.BytesIO(archive.read(name))).size == (800, 600)


def test_payment_permissions_upsert_and_filter(world):
    group = SubmissionSet.objects.create(
        user=world.owner, author=world.author, contest=world.contest
    )
    data = {"submissionset": group.pk, "paid": True}
    assert world.client.post("/api/payment/", data, format="json").status_code == 403
    world.client.force_authenticate(world.admin)
    assert world.client.post("/api/payment/", data, format="json").status_code == 201
    data["paid"] = False
    assert world.client.post("/api/payment/", data, format="json").status_code == 201
    assert Payment.objects.count() == 1
    assert not Payment.objects.get().paid
    assert rows(world.client.get("/api/payment/", {"paid": "true"})) == []


def test_judging_uses_postgres_ordering_and_scopes_paid_submissions(world):
    judge = Judge.objects.create(judge=world.owner, contest=world.contest)
    item = submitted(world, user=world.other, author=world.other_author)
    group = SubmissionSet.objects.create(
        user=world.other, author=world.other_author, contest=world.contest
    )
    group.submissions.add(item)
    Payment.objects.create(submissionset=group, paid=True)
    unpaid = submitted(world)
    response = world.client.get("/api/judge/submission/")
    assert response.status_code == 200, response.data
    assert [row["id"] for row in rows(response)] == [item.pk]
    other_theme = Theme.objects.create(contest=world.contest, title="Empty", n_photos=4)
    assert (
        rows(world.client.get("/api/judge/submission/", {"theme": other_theme.pk}))
        == []
    )
    for value in [3, 5]:
        response = world.client.post(
            "/api/rating/", {"submission": item.pk, "rating": value}, format="json"
        )
        assert response.status_code == 201, response.data
    assert Rating.objects.get(judge=judge, submission=item).rating == 5
    assert rows(world.client.get("/api/rating/", {"submission": unpaid.pk})) == []


def test_anonymous_judge_endpoint_denies_without_server_error(world):
    response = APIClient().get("/api/judge/submission/")
    assert response.status_code in (401, 403)


def test_rating_updates_cannot_move_rating_to_another_contest(world):
    Judge.objects.create(judge=world.owner, contest=world.contest)
    item = submitted(world)
    response = world.client.post(
        "/api/rating/", {"submission": item.pk, "rating": 3}, format="json"
    )
    assert response.status_code == 201
    contest = Contest.objects.create(
        title="Other contest",
        start_date=world.contest.start_date,
        end_date=world.contest.end_date,
    )
    theme = Theme.objects.create(contest=contest, title="Other", n_photos=4)
    other = submitted(world, theme=theme)
    response = world.client.patch(
        f"/api/rating/{response.data['id']}/", {"submission": other.pk}, format="json"
    )
    assert response.status_code == 400


def test_results_hide_before_publication_and_handle_optional_relations(world):
    item = submitted(world)
    judge = Judge.objects.create(judge=world.other, contest=world.contest)
    Rating.objects.create(user=world.other, judge=judge, submission=item, rating=5)
    ThemeResults.objects.create(theme=world.theme, accepted_threshold=3)
    SubmissionReward.objects.create(submission=item, kind=1, label="Gold")
    public = APIClient()
    assert rows(public.get("/api/results/submission/")) == []
    world.contest.publish_date = timezone.now() - timedelta(seconds=1)
    world.contest.save()
    response = public.get("/api/results/submission/")
    assert response.status_code == 200, response.data
    assert rows(response)[0]["accepted"] is True
    assert rows(response)[0]["author"]["country"] is None
    assert rows(response)[0]["author"]["email"] is None
    assert rows(response)[0]["reward_kind"] == "Gold"


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_published_scores_are_immutable(world, method):
    judge = Judge.objects.create(judge=world.owner, contest=world.contest)
    item = submitted(world)
    rating = Rating.objects.create(
        judge=judge, user=world.owner, submission=item, rating=4
    )
    world.contest.publish_date = timezone.now() - timedelta(seconds=1)
    world.contest.save()
    response = getattr(world.client, method)(
        f"/api/rating/{rating.pk}/", {"rating": 1}, format="json"
    )
    assert response.status_code == 403
    rating.refresh_from_db()
    assert rating.rating == 4
