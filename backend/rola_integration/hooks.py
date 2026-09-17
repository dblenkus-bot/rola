"""Implement optional Rolca behavior using Rola's account models."""

from rolca.core.models import Author, SubmissionSet

from .models import ContestNotification


def send_submission_confirmation(submission_set: SubmissionSet) -> None:
    """Send the contest template to the submitting account.

    Parameters
    ----------
    submission_set : SubmissionSet
        Committed submission group whose owner receives the confirmation.
    """
    user = submission_set.user
    if user is None or not user.email:
        return
    configuration = (
        ContestNotification.objects.using(submission_set._state.db)
        .filter(contest_id=submission_set.contest_id)
        .select_related("confirmation_email")
        .first()
    )
    if configuration is not None and configuration.confirmation_email is not None:
        configuration.confirmation_email.send(user.email)


def get_author_country(author: Author) -> str | None:
    """Read the country supplied by the account's optional location.

    Parameters
    ----------
    author : Author
        Contest author whose account and location have been preloaded.

    Returns
    -------
    str or None
        Account country, or ``None`` when either relationship is absent.
    """
    if author.user is None or author.user.location is None:
        return None
    return author.user.location.country
