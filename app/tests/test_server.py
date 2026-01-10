"""Tests for FastAPI server endpoints"""

import pytest
from unittest.mock import MagicMock, patch


class TestGetEndpoint:
    """Test GET / endpoint"""

    def test_get_root_returns_index_html(self, test_client):
        """GET / returns index.html"""
        response = test_client.get("/")

        # Should return 200 OK
        assert response.status_code == 200

        # Should return HTML content
        assert response.headers["content-type"].startswith("text/html")


class TestCaptureEndpoint:
    """Test POST /api/capture endpoint"""

    def test_post_capture_valid_json(self, test_client):
        """POST /api/capture (Valid JSON): Request with valid JSON returns success"""
        response = test_client.post("/api/capture", json={"text": "pl3"})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data

    def test_post_capture_missing_field(self, test_client):
        """POST /api/capture (Missing Field): Request missing 'text' field returns 422 validation error"""
        response = test_client.post("/api/capture", json={})

        # FastAPI returns 422 for validation errors
        assert response.status_code == 422

    def test_post_capture_empty_string(self, test_client):
        """POST /api/capture (Empty String): Empty string is handled appropriately"""
        response = test_client.post("/api/capture", json={"text": ""})

        # Should still return success - empty string is valid
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_post_capture_response_format(self, test_client):
        """POST /api/capture (Response Format): Response has correct format with 'status' and 'message' fields"""
        response = test_client.post("/api/capture", json={"text": "test text"})

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "status" in data
        assert "message" in data
        assert data["status"] == "success"
        assert isinstance(data["message"], str)

    def test_post_capture_background_task(self, test_client, monkeypatch):
        """POST /api/capture (Background Task): Background task is triggered with correct arguments"""
        # Mock the quick_capture.process method to verify it's called
        mock_process = MagicMock()

        import server
        original_process = server.quick_capture.process
        monkeypatch.setattr(server.quick_capture, 'process', mock_process)

        # Make the request
        test_text = "pl5"
        response = test_client.post("/api/capture", json={"text": test_text})

        # Verify response is successful
        assert response.status_code == 200

        # Verify that quick_capture.process was called with the correct text
        # Note: TestClient executes background tasks synchronously
        mock_process.assert_called_once_with(test_text)
