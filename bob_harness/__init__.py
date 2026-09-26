"""sipa-bob-sprint harness: run IBM Bob (bob run --format stream-json),
turn every tool_use/tool_result event into a sipa-trace TraceCard
(structured, diffable, risk-classified — not prose you have to re-read),
and clean up Bob's own text explanations through sipa-signal (strip
hedging/filler into a fixed-schema SignalCard) before showing them to a
human.

Use case: "Intelligent code review and quality coach" (from the official
IBM Bob 2.0 Hackathon example list) — Bob does the review, this harness
makes the review verifiable and diffable instead of a paragraph you have
to trust on read.
"""
from . import _pathsetup  # noqa: F401 — must run before sipa_trace/sipa_signal imports
from .risk_map import classify_tool_call
from .runner import run_bob_task, BobRunResult

__all__ = ["classify_tool_call", "run_bob_task", "BobRunResult"]
