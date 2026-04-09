import sys
from pathlib import Path

# Include src directory in Python path for module resolution in ASGI deployment
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.main import app

__all__ = ["app"]
