"""Runs a Bob task headlessly, streams its stream-json output, and turns it
into two artifacts:
  - a sipa-trace TraceLog (trace.jsonl) — one TraceCard per tool call Bob
    made, hash-chained and risk-classified. Diffable, not prose.
  - a sipa-signal pass over Bob's own assistant text — the final answer is
    stripped of hedging/filler into a fixed-schema SignalCard before a
    human has to read it.

This is the "quality coach" wiring: Bob does the review, this module makes
the review verifiable and quiet instead of a paragraph you have to trust.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from sipa_trace import RiskClassifier, TraceLog
from sipa_signal import extract as signal_extract

from .risk_map import classify_tool_call

_classifier = RiskClassifier()


@dataclass
class BobRunResult:
    task_id: str | None
    status: str
    duration_ms: int | None
    session_cost: float | None
    tool_calls: int
    trace_cards_written: int
    assistant_text: str
    signal_card: dict  # sipa_signal.SignalCard.to_dict()
    raw_events: list[dict] = field(default_factory=list)


def _iter_bob_events(proc: subprocess.Popen):
    for raw_line in proc.stdout:
        line = raw_line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            # Bob occasionally emits non-JSON status lines on stdout (e.g.
            # experimental-feature warnings) — skip rather than crash the
            # whole task on one bad line.
            continue


def run_bob_task(
    prompt: str,
    workspace: str | Path,
    trace_log_path: str | Path,
    *,
    stage: str = "bob_review",
    accept_license: bool = True,
    disable_mcp: bool = True,
    trust: bool = True,
    timeout_s: int = 300,
    bob_bin: str = "bob",
) -> BobRunResult:
    """Run one Bob task in headless mode and record it into sipa-trace +
    sipa-signal. Raises subprocess.TimeoutExpired if Bob exceeds timeout_s
    — callers should catch this rather than let a stuck task hang the
    whole harness run.
    """
    workspace = str(workspace)
    log = TraceLog(trace_log_path)

    cmd = [bob_bin, "run", prompt, "--format", "stream-json", "--workspace", workspace]
    if accept_license:
        cmd.append("--accept-license")
    if disable_mcp:
        cmd.append("--disable-mcp")
    if trust:
        cmd.append("--trust")

    proc = subprocess.Popen(
        cmd, cwd=workspace, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1,
    )

    raw_events: list[dict] = []
    assistant_text_parts: list[str] = []
    trace_cards_written = 0
    task_id = None
    status = "unknown"
    duration_ms = None
    session_cost = None
    tool_calls_total = 0

    try:
        for event in _iter_bob_events(proc):
            raw_events.append(event)
            etype = event.get("type")

            if etype == "message" and event.get("role") == "assistant":
                assistant_text_parts.append(event.get("content", ""))

            elif etype == "tool_use":
                profile = classify_tool_call(event.get("tool_name", ""), event.get("parameters", {}) or {})
                risk_class = _classifier.classify(profile)
                state_delta = _classifier.state_delta(profile)
                log.append(
                    stage=stage,
                    action_type=f"bob_tool:{event.get('tool_name', 'unknown')}",
                    inputs_digest=_short_digest(event.get("parameters", {})),
                    outputs_digest=_short_digest(event.get("tool_id", "")),
                    risk_class=risk_class,
                    reversible=profile.reversible,
                    state_delta=state_delta,
                )
                trace_cards_written += 1

            elif etype == "result":
                stats = event.get("stats", {}) or {}
                task_id = stats.get("task_id")
                status = event.get("status", "unknown")
                duration_ms = stats.get("duration_ms")
                session_cost = stats.get("session_costs")
                tool_calls_total = stats.get("tool_calls", trace_cards_written)

        proc.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        proc.kill()
        raise

    assistant_text = "".join(assistant_text_parts)
    signal_card = signal_extract(assistant_text).to_dict() if assistant_text else {}

    return BobRunResult(
        task_id=task_id,
        status=status,
        duration_ms=duration_ms,
        session_cost=session_cost,
        tool_calls=tool_calls_total,
        trace_cards_written=trace_cards_written,
        assistant_text=assistant_text,
        signal_card=signal_card,
        raw_events=raw_events,
    )


def _short_digest(value) -> str:
    from sipa_trace.card import digest
    return digest(value)
