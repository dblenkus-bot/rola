"""Keep list serialization queries bounded as related data grows."""

import hashlib
from types import SimpleNamespace

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from rolca.core.models import Author, SubmissionSet, Theme
from rolca.payment.models import Payment
from rolca.rating.models import Judge, Rating
from tests.factories import photo, submitted

pytestmark = pytest.mark.django_db


def _rows(response):
    return (
        response.data["results"] if isinstance(response.data, dict) else response.data
    )


def _entry(world, judge, index):
    author = Author.objects.create(
        user=world.owner, first_name=f"Author {index}", last_name="Photographer"
    )
    theme = Theme.objects.create(
        contest=world.contest, title=f"Theme {index}", n_photos=4
    )
    submission = submitted(world, author=author, theme=theme, title=f"Photo {index}")
    files = [photo(world.owner), photo(world.owner)]
    submission.files.add(*files)
    group = SubmissionSet.objects.create(
        user=world.owner, author=author, contest=world.contest
    )
    group.submissions.add(submission)
    Payment.objects.create(submissionset=group, paid=True)
    Rating.objects.create(
        user=world.owner, judge=judge, submission=submission, rating=5
    )
    return SimpleNamespace(
        author=author, theme=theme, submission=submission, group=group, files=files
    )


def _assert_submission(data, entry, email):
    assert data["id"] == entry.submission.pk
    assert data["title"] == entry.submission.title
    assert data["theme"] == entry.theme.pk
    assert data["author"]["id"] == entry.author.pk
    assert data["author"]["first_name"] == entry.author.first_name
    assert data["author"]["email"] == email
    assert [item["id"] for item in data["files"]] == [file.pk for file in entry.files]
    assert all(item["file"] and item["thumbnail"] for item in data["files"])


@pytest.mark.parametrize(
    "endpoint",
    [
        "author",
        "contest",
        "submission",
        "submissionset",
        "judge/contest",
        "judge/submission",
    ],
)
def test_list_queries_do_not_grow_with_related_objects(world, endpoint):
    """Adding related rows preserves response content and the query budget."""
    judge = Judge.objects.create(judge=world.owner, contest=world.contest)
    if endpoint == "author":
        world.client.force_authenticate(world.admin)
    entries = []
    query_counts = []
    for count in (1, 4):
        start = len(entries)
        entries.extend(_entry(world, judge, i) for i in range(start, start + count))
        with CaptureQueriesContext(connection) as queries:
            response = world.client.get(f"/api/{endpoint}/")
        assert response.status_code == 200, response.data
        query_counts.append(len(queries))
        data = _rows(response)

        if endpoint == "author":
            authors = [world.author, world.other_author] + [
                entry.author for entry in entries
            ]
            assert [item["id"] for item in data] == [author.pk for author in authors]
            assert [item["email"] for item in data] == [
                world.owner.email,
                world.other.email,
                *[world.owner.email for _ in entries],
            ]
        elif endpoint in ("contest", "judge/contest"):
            assert [item["id"] for item in data] == [world.contest.pk]
            themes = data[0]["themes"]
            assert [theme["id"] for theme in themes] == [
                world.theme.pk,
                *[entry.theme.pk for entry in entries],
            ]
            assert [theme["submissions_number"] for theme in themes] == [
                0,
                *[1 for _ in entries],
            ]
            if endpoint == "judge/contest":
                assert [theme["ratings_number"] for theme in themes] == [
                    0,
                    *[1 for _ in entries],
                ]
        elif endpoint == "submissionset":
            assert [item["id"] for item in data] == [
                entry.group.pk for entry in entries
            ]
            for item, entry in zip(data, entries, strict=True):
                assert item["author"]["id"] == entry.author.pk
                assert item["author"]["email"] is None
                assert item["contest"] == world.contest.pk
                assert len(item["submissions"]) == 1
                _assert_submission(item["submissions"][0], entry, None)
        else:
            expected = entries
            if endpoint == "judge/submission":
                expected = sorted(
                    entries,
                    key=lambda entry: hashlib.sha1(
                        f"{entry.submission.pk}{world.owner.pk}".encode()
                    ).hexdigest(),
                )
            assert [item["id"] for item in data] == [
                entry.submission.pk for entry in expected
            ]
            for item, entry in zip(data, expected, strict=True):
                _assert_submission(item, entry, None)

    assert query_counts[1] == query_counts[0]


def test_judging_counts_keep_payments_and_judges_independent(world):
    """Paid-set joins and other judges cannot multiply the rating count."""
    judge = Judge.objects.create(judge=world.owner, contest=world.contest)
    other_judge = Judge.objects.create(judge=world.other, contest=world.contest)
    first, second, unpaid = (submitted(world) for _ in range(3))
    for submission in (first, first, second):
        group = SubmissionSet.objects.create(
            user=world.owner, author=world.author, contest=world.contest
        )
        group.submissions.add(submission)
        Payment.objects.create(submissionset=group, paid=True)
    for submission in (first, unpaid):
        Rating.objects.create(
            user=world.owner, judge=judge, submission=submission, rating=5
        )
    for submission in (first, second):
        Rating.objects.create(
            user=world.other, judge=other_judge, submission=submission, rating=3
        )
    empty = Theme.objects.create(contest=world.contest, title="Empty", n_photos=4)

    response = world.client.get("/api/judge/contest/")
    assert response.status_code == 200, response.data
    themes = _rows(response)[0]["themes"]
    assert [theme["id"] for theme in themes] == [world.theme.pk, empty.pk]
    assert [theme["submissions_number"] for theme in themes] == [3, 0]
    assert [theme["ratings_number"] for theme in themes] == [2, 0]

    response = world.client.get("/api/contest/")
    assert response.status_code == 200, response.data
    assert [theme["submissions_number"] for theme in _rows(response)[0]["themes"]] == [
        3,
        0,
    ]
