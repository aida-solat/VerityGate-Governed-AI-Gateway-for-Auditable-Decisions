"""Test configuration.

Point the ledger at a throwaway SQLite file BEFORE the app is imported, so
tests never touch the dev database. config.get_settings() is cached, so the
env var must be set at collection time (which conftest guarantees).
"""
import os
import tempfile

_tmp_db = os.path.join(tempfile.gettempdir(), "veritygate_test.db")
if os.path.exists(_tmp_db):
    os.remove(_tmp_db)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db}"

import pytest
from fastapi.testclient import TestClient

from app.db import init_db
from app.main import app


@pytest.fixture(scope="session")
def client():
    init_db()
    with TestClient(app) as c:
        yield c
