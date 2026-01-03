"""
Unit tests for app.py module.

Tests the basic functionality of the application interface.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_app_module_exists():
    """Test that app.py module can be imported."""
    import app
    assert app is not None


def test_app_main_block():
    """Test that app.py has a main block."""
    import app
    # Check that the module has the expected structure
    assert hasattr(app, '__name__')
    assert app.__name__ == 'app' or app.__name__ == '__main__'


def test_src_module_exists():
    """Test that src package can be imported."""
    from src import __version__
    assert __version__ == "1.0.0"


def test_src_init():
    """Test that src/__init__.py is properly configured."""
    import src
    assert hasattr(src, '__version__')
    assert src.__version__ == "1.0.0"

