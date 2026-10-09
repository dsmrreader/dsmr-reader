import pytest
from django.contrib.auth.models import User
from django.core.management import call_command

FRONTEND_FIXTURES = [
    "dsmr_frontend/test_dsmrreading.json",
    "dsmr_frontend/test_note.json",
    "dsmr_frontend/test_energysupplierprice.json",
    "dsmr_frontend/test_statistics.json",
    "dsmr_frontend/test_meterstatistics.json",
    "dsmr_frontend/test_electricity_consumption.json",
    "dsmr_frontend/test_gas_consumption.json",
]


@pytest.fixture(scope="session", autouse=True)
def allow_async_unsafe_orm():
    """Playwright's sync API keeps an event loop running in the test thread, which Django's ORM refuses to run in.

    Session-scoped, as pytest-django's session-scoped database setup needs it as well.
    """
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
        yield


@pytest.fixture
def frontend_data(transactional_db):
    """Loads a representative dataset so pages render charts/tables with real content.

    Uses transactional_db (not db) because live_server serves requests from a separate
    thread and can only see data committed to the database, not data held in the db
    fixture's uncommitted transaction.
    """
    call_command("loaddata", *FRONTEND_FIXTURES)


@pytest.fixture
def admin_credentials(transactional_db):
    username, password = "e2e-admin", "e2e-password"
    User.objects.create_superuser(username, "e2e-admin@localhost", password)
    return username, password
