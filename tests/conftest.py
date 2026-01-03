"""
Pytest configuration and fixtures for the test suite.

This file is automatically discovered by pytest and provides shared
fixtures and configuration for all tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root directory as a Path object."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root_path):
    """Return the test data directory path."""
    return project_root_path / "data"


@pytest.fixture(autouse=True)
def reset_path():
    """Reset sys.path after each test if needed."""
    yield
    # Any cleanup can go here if needed

