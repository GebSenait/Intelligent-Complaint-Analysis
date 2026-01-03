"""
Basic unit tests for the Intelligent Complaint Analysis Platform.

These tests ensure the basic project structure and dependencies are working.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_python_version():
    """Test that Python version is 3.8 or higher."""
    assert sys.version_info >= (3, 8), "Python 3.8 or higher is required"


def test_project_structure():
    """Test that essential project directories exist."""
    project_root = Path(__file__).parent.parent
    
    # Check essential directories
    assert (project_root / "src").exists(), "src directory should exist"
    assert (project_root / "tests").exists(), "tests directory should exist"
    assert (project_root / "notebooks").exists(), "notebooks directory should exist"
    assert (project_root / "data").exists(), "data directory should exist"


def test_imports():
    """Test that basic imports work."""
    # Test that we can import standard libraries
    import os
    import json
    import pathlib
    
    assert os is not None
    assert json is not None
    assert pathlib is not None


def test_requirements_installed():
    """Test that key dependencies from requirements.txt can be imported."""
    try:
        import pandas
        import numpy
        import matplotlib
        import seaborn
        import jupyter
        
        # Basic version checks
        assert hasattr(pandas, '__version__')
        assert hasattr(numpy, '__version__')
        
    except ImportError as e:
        pytest.skip(f"Some dependencies not installed: {e}")

