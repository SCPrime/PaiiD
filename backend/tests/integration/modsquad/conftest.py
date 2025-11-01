"""Conftest for modsquad integration tests - ensures modsquad module is importable."""
import sys
from pathlib import Path

# Add repository root to Python path for modsquad imports
repo_root = Path(__file__).parent.parent.parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
