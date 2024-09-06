import pytest
from fastapi import status
from unittest.mock import AsyncMock, Mock


from app.models import Event


@pytest.mark.asyncio
async def test_create_event_success(test_client, mock_db_session):
	"""
    Test the successful creation of an event.
    """
	# Sample request payload
	payload = {
		"title": "Test Event",
		"message": "This is a test event"
	}

	# Mocking the database session for commit and add
	mock_db_session.commit = AsyncMock()
	mock_db_session.add = Mock()

	response = test_client.put("/v1/test_bucket/", json=payload)

	assert response.status_code == status.HTTP_200_OK
	json_response = response.json()
	assert "event_id" in json_response
	mock_db_session.add.assert_called_once()  # Ensure event was added to the session
	mock_db_session.commit.assert_called_once()  # Ensure commit was called


@pytest.mark.asyncio
async def test_list_event_ids_success(test_client, mock_db_session):
	"""
    Test listing event IDs in a bucket.
    """
	# Mocking the database response for select query
	mock_result = Mock()  # Regular Mock, as scalars() is not async

	# Mock scalars() to return a Mock that has all() returning your test values
	mock_result.scalars.return_value.all.return_value = ["event1", "event2"]

	# Set the result of db.execute() to return mock_result
	mock_db_session.execute.return_value = mock_result

	response = test_client.get("/v1/test_bucket/")

	assert response.status_code == status.HTTP_200_OK
	json_response = response.json()
	assert "event_ids" in json_response
	assert json_response["event_ids"] == ["event1", "event2"]


@pytest.mark.asyncio
async def test_get_event_success(test_client, mock_db_session):
	"""
	Test retrieving a specific event by event_id.
	"""
	# Mock the event object returned from the database query
	mock_event = Event(event_id="event1", bucket_id="test_bucket", title="Test Event", message="This is a test event")
	mock_result = Mock()
	mock_result.scalars.return_value.first.return_value = mock_event
	mock_db_session.execute = AsyncMock(return_value=mock_result)

	response = test_client.get("/v1/test_bucket/event1")

	assert response.status_code == status.HTTP_200_OK
	json_response = response.json()
	assert json_response["ID"] == "event1"
	assert json_response["title"] == "Test Event"
	assert json_response["message"] == "This is a test event"


@pytest.mark.asyncio
async def test_get_event_not_found(test_client, mock_db_session):
	"""
	Test retrieving a specific event by event_id that does not exist.
	"""
	# Mock the database query to return None
	mock_result = Mock()
	mock_result.scalars.return_value.first.return_value = None
	mock_db_session.execute = AsyncMock(return_value=mock_result)

	response = test_client.get("/v1/test_bucket/invalid_event")

	assert response.status_code == status.HTTP_404_NOT_FOUND
	json_response = response.json()
	assert json_response["detail"] == "Event not found"


@pytest.mark.asyncio
async def test_list_event_ids_empty(test_client, mock_db_session):
	"""
	Test listing event IDs when no events exist in the bucket.
	"""
	mock_result = Mock()  # scalars() is not async, so use Mock

	# Mock scalars() to return an empty list when all() is called
	mock_result.scalars.return_value.all.return_value = []  # Return an empty list

	# Assign the mock result to db.execute() (async)
	mock_db_session.execute.return_value = mock_result

	# Perform the request
	response = test_client.get("/v1/test_bucket/")

	assert response.status_code == 404
	json_response = response.json()
	assert json_response["detail"] == "No events found in this bucket"
	mock_db_session.execute.assert_called_once()  # Ensure the query was called

