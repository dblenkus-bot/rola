"""Check that the configured databases accept queries."""

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.utils import DatabaseError


def check_database():
    """Query every configured database and close its cursor."""
    for name in connections:
        try:
            with connections[name].cursor() as cursor:
                cursor.execute("SELECT 1")
                if cursor.fetchone() != (1,):
                    raise CommandError(f"Database {name} returned an invalid response.")
        except DatabaseError as error:
            raise CommandError(f"Database {name} is unavailable.") from error


class Command(BaseCommand):
    """Run the database readiness checks."""

    help = "Check database readiness."

    def handle(self, *args, **options):
        """Fail when any configured database cannot answer a query."""
        check_database()
