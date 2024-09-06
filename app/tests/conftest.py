import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

from app.main import app, get_db  # Import your FastAPI app and get_db dependency


@pytest.fixture()
def test_client(mock_db_session):
    """Fixture for test client."""
    app.dependency_overrides[get_db] = lambda: mock_db_session
    client = TestClient(app)
    return client


@pytest.fixture()
def mock_db_session(monkeypatch):
    """
    Fixture for mocking the AsyncSession dependency using monkeypatch.
    """
    # Mock the session and database calls
    mock_session = AsyncMock(spec=AsyncSession)

    # Mock the return value of `get_db` dependency to use the mocked session
    async def mock_get_db():
        yield mock_session

    # Monkeypatch the `get_db` dependency to return the mocked session
    monkeypatch.setattr("app.main.get_db", mock_get_db)

    return mock_session
