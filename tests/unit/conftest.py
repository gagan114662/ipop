"""Pytest configuration for unit tests.

Unit tests should not depend on external services like MongoDB, Redis, etc.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
