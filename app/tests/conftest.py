"""Shared pytest fixtures for Obsidian Enhanced tests"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def mock_vault_handler():
    """Create a MagicMock for VaultHandler

    Returns:
        MagicMock: Mocked VaultHandler instance with all methods mocked
    """
    mock = MagicMock()
    mock.vault_path = "/vault"
    return mock


@pytest.fixture
def quick_capture_instance(mock_vault_handler):
    """Create a QuickCapture instance with mocked VaultHandler

    Args:
        mock_vault_handler: Fixture providing mocked VaultHandler

    Returns:
        QuickCapture: Instance with mocked dependencies
    """
    from quick_capture import QuickCapture
    return QuickCapture(mock_vault_handler)


@pytest.fixture
def test_client(monkeypatch):
    """Create a FastAPI TestClient with mocked dependencies

    Args:
        monkeypatch: pytest fixture for patching

    Returns:
        TestClient: FastAPI test client for API testing
    """
    # Mock the VaultHandler to avoid real vault operations
    mock_vault = MagicMock()
    mock_vault.vault_path = "/vault"

    # Patch the vault_handler and quick_capture in the server module
    from quick_capture import QuickCapture
    mock_quick_capture = QuickCapture(mock_vault)

    # Import and patch the server module
    import server
    monkeypatch.setattr(server, 'vault_handler', mock_vault)
    monkeypatch.setattr(server, 'quick_capture', mock_quick_capture)

    # Create and return test client
    from fastapi.testclient import TestClient
    return TestClient(server.app)
