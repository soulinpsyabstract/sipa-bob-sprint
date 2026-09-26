import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # .../apps/
_THIS_PROJECT = Path(__file__).resolve().parent.parent       # .../sipa-bob-sprint/
for _p in (_REPO_ROOT / "sipa-trace", _REPO_ROOT / "sipa-signal", _THIS_PROJECT):
    _p = str(_p)
    if _p not in sys.path:
        sys.path.insert(0, _p)
