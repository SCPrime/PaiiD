"""
MOD SQUAD Auto-Startup Configuration
Loaded automatically on every Python session
"""

import sys
from pathlib import Path

# Add MOD SQUAD to path
project_root = Path.cwd()
modsquad_path = project_root / "modsquad"

if modsquad_path.exists():
    sys.path.insert(0, str(modsquad_path))
    sys.path.insert(0, str(project_root / "backend"))

    try:
        # Import and activate MOD SQUAD
        import modsquad

        # ALPHA SQUAD auto-activates on import
        print(f"MOD SQUAD v{modsquad.__version__} loaded")
        print(f"   ALPHA SQUAD: Active (always-on services)")
        print(f"   BRAVO SQUAD: 7 quality guardrail extensions")
        print(f"      - Visual: Playwright + Argos (Percy eliminated)")
        print(f"      - Advanced: Design DNA, Focus States, Component Isolation")
        print(f"      - Guardrails: Accessibility, Performance, Bundle, Runtime")
        print(f"   SUN TZU SQUAD: Strategic batch planning (5 extensions)")
        print(f"      - The Art of Parallel Warfare: 20-60% speedup via batching")
        print(f"   ARMANI SQUAD: Integration weaving (6 extensions)")
        print(f"      - Haute Couture Code Integration: Atomic rollback + validation")
        print(f"   Available squads: bravo, charlie, delta, echo, foxtrot, sun_tzu, armani")
        print(f"   Quick start: modsquad.squad_status()")

    except ImportError as e:
        print(f"MOD SQUAD import failed: {e}")
