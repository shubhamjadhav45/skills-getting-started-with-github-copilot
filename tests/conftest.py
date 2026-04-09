"""
Test configuration and fixtures for FastAPI tests.
Provides pytest fixtures with sample data and test client setup.
"""

import pytest
from copy import deepcopy
from starlette.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient instance for making requests to the app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    original_activities = deepcopy(activities)
    yield
    # Reset to original state after test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_activity():
    """Provide a sample activity name for testing."""
    return "Chess Club"


@pytest.fixture
def sample_email():
    """Provide a sample email for testing."""
    return "test.student@mergington.edu"


@pytest.fixture
def sample_new_email():
    """Provide another sample email for testing."""
    return "new.student@mergington.edu"
