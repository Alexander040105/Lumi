"""Project-wide conftest for LUMI tests.

Makes the fastapi-backend package and its app/services submodules importable
regardless of where pytest is invoked from.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_DIR = REPO_ROOT / "fastapi-backend"
SERVICES_DIR = FASTAPI_DIR / "app" / "services"

# fastapi-backend/ makes `from app.x.y` imports resolve
sys.path.insert(0, str(FASTAPI_DIR))

# fastapi-backend/app/services/ makes `import solar_output_calc` style imports resolve
sys.path.insert(0, str(SERVICES_DIR))
