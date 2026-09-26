"""Add sipa-trace and sipa-signal source roots to sys.path so bob_harness
can import them without needing an editable pip install (both packages are
pure-Python, zero-dependency — no need for a venv here). Import this module
before importing anything from bob_harness that touches sipa_trace/sipa_signal.
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # .../apps/
for _name in ("sipa-trace", "sipa-signal"):
    _p = str(_REPO_ROOT / _name)
    if _p not in sys.path:
        sys.path.insert(0, _p)
