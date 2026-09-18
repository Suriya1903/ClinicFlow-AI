import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client():
    """
    Create a FastAPI test client.

    Lifespan events are intentionally not started here because
    these basic API tests do not require the scheduler or MCP
    session manager to be running.
    """

    test_client = TestClient(app)

    try:
        yield test_client
    finally:
        test_client.close()