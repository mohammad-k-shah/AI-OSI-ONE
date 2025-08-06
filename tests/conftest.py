"""
Pytest Configuration and Common Fixtures

This file contains shared fixtures and configuration for all tests.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from pathlib import Path

# Add src to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def mock_config():
    """Mock configuration manager."""
    config = Mock()
    config.get.return_value = "test_value"
    config.get_nlp_config.return_value = {
        "provider": "openai",
        "model": "gpt-4",
        "max_tokens": 1000
    }
    return config


@pytest.fixture
def mock_token_manager():
    """Mock token manager."""
    token_manager = Mock()
    token_manager.get_token.return_value = "test_token"
    token_manager.encrypt_token.return_value = "encrypted_token"
    token_manager.decrypt_token.return_value = "decrypted_token"
    return token_manager


@pytest.fixture
def mock_agent():
    """Mock agent orchestrator."""
    agent = Mock()
    agent.process_query = AsyncMock(return_value={"result": "success"})
    agent.get_tools = Mock(return_value=["azure_devops", "osi_one", "teams"])
    return agent


@pytest.fixture
def sample_user_query():
    """Sample user query for testing."""
    return "Show my tasks for this sprint"


@pytest.fixture
def sample_azure_devops_response():
    """Sample Azure DevOps API response."""
    return {
        "count": 2,
        "value": [
            {
                "id": 123,
                "title": "Implement new feature",
                "state": "Active",
                "assignedTo": "user@osi-digital.com"
            },
            {
                "id": 124,
                "title": "Fix bug in login",
                "state": "Active",
                "assignedTo": "user@osi-digital.com"
            }
        ]
    }


@pytest.fixture
def sample_calendar_response():
    """Sample Microsoft Graph calendar response."""
    return {
        "value": [
            {
                "id": "event1",
                "subject": "Team Meeting",
                "start": {"dateTime": "2024-01-15T10:00:00Z"},
                "end": {"dateTime": "2024-01-15T11:00:00Z"},
                "attendees": [
                    {"emailAddress": {"address": "user@osi-digital.com"}}
                ]
            }
        ]
    }


# Async test support
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 