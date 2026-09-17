"""Explicit hooks for optional host application behavior."""

from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.db import transaction
from django.utils.module_loading import import_string

from rolca.core.models import Author, SubmissionSet


def _callback(setting: str) -> Callable[..., Any] | None:
    path = getattr(settings, setting, None)
    return import_string(path) if path else None


def schedule_submission_confirmation(submission_set: SubmissionSet) -> None:
    """Run the configured confirmation callback after the submission commits.

    Parameters
    ----------
    submission_set : SubmissionSet
        Persisted group passed to the host callback after a successful commit.
    """
    callback = _callback("ROLCA_SUBMISSION_CONFIRMATION_CALLBACK")
    if callback is None:
        return

    def notify() -> None:
        callback(submission_set)

    transaction.on_commit(notify, using=submission_set._state.db, robust=True)


def get_author_country(author: Author) -> str | None:
    """Resolve an author's country through the optional host callback.

    Parameters
    ----------
    author : Author
        Author whose optional country is being serialized.

    Returns
    -------
    str or None
        Host country value, or ``None`` when no callback is configured.
    """
    callback = _callback("ROLCA_AUTHOR_COUNTRY_CALLBACK")
    return callback(author) if callback else None


def author_select_related(prefix: str) -> tuple[str, ...]:
    """Build result-query joins from the configured author-relative paths.

    Parameters
    ----------
    prefix : str
        Queryset relationship leading to the author.

    Returns
    -------
    tuple of str
        User relationship and any host-defined single-valued relationships.
    """
    paths = ("user", *getattr(settings, "ROLCA_AUTHOR_SELECT_RELATED", ()))
    return tuple(f"{prefix}__{path}" for path in dict.fromkeys(paths))
