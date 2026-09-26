"""Unit tests for classify_tool_call — the generic tool→ActionProfile map.
No Bob calls here; these test the deterministic classification logic only.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sipa_trace import RiskClass, RiskClassifier
from bob_harness.risk_map import classify_tool_call

_classifier = RiskClassifier()


def _classify(tool_name, params):
    return _classifier.classify(classify_tool_call(tool_name, params))


def test_read_only_tool_is_none_risk():
    assert _classify("read_file", {"path": "calc.py"}) == RiskClass.NONE


def test_write_tool_is_low_risk():
    assert _classify("write_file", {"path": "calc.py", "content": "x = 1"}) == RiskClass.LOW


def test_delete_tool_is_critical_risk():
    # delete_file is always marked non-reversible in our map, and
    # sipa_trace's classifier scores deletes_data + not reversible as
    # CRITICAL (its most conservative bucket) — correct, not a bug.
    assert _classify("delete_file", {"path": "calc.py"}) == RiskClass.CRITICAL


def test_exec_with_destructive_shell_is_critical_or_high():
    # deletes_data + not reversible -> CRITICAL under sipa_trace's classifier
    result = _classify("execute_command", {"command": "rm -rf /tmp/something"})
    assert result == RiskClass.CRITICAL


def test_exec_benign_command_is_low_or_medium():
    result = _classify("execute_command", {"command": "pytest tests/"})
    # writes_data=True (exec treated as write-capable) -> at least LOW
    assert result >= RiskClass.LOW


def test_network_tool_is_medium_risk():
    assert _classify("web_fetch", {"url": "https://example.com"}) == RiskClass.MEDIUM


def test_credential_mention_escalates_to_medium_or_critical():
    result = _classify("read_file", {"path": ".env", "content_hint": "API_KEY=secret123"})
    assert result >= RiskClass.MEDIUM


def test_unknown_tool_falls_through_to_none_not_silently_high():
    assert _classify("some_future_tool_bob_adds", {"whatever": 1}) == RiskClass.NONE


def test_reversibility_flag_survives_for_delete():
    profile = classify_tool_call("delete_file", {"path": "x.py"})
    assert profile.reversible is False


def test_reversibility_flag_true_for_write():
    profile = classify_tool_call("write_file", {"path": "x.py"})
    assert profile.reversible is True
