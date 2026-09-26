#!/usr/bin/env python3
"""Real end-to-end demo: runs Bob on a sample repo, records every tool call
into sipa-trace (trace.jsonl), and shows Bob's cleaned-up explanation via
sipa-signal. No fake data — this actually calls `bob run` and spends real
Bobcoins (a fraction of one task's worth per demo run).

Usage: python3 run_demo.py [workspace_dir]
Requires: bob CLI installed + authenticated (see governance doc), and
this repo's bob_harness importable (run from repo root).
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bob_harness import run_bob_task
from sipa_trace import TraceLog


def main():
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp(prefix="bob_demo_"))
    workspace.mkdir(parents=True, exist_ok=True)

    sample_file = workspace / "calc.py"
    if not sample_file.exists():
        sample_file.write_text("def add(a, b):\n    return a + b\n")

    trace_path = workspace / "trace.jsonl"

    print(f"Workspace: {workspace}")
    print(f"Trace log: {trace_path}")
    print("Running Bob task (this spends real Bobcoins)...\n")

    result = run_bob_task(
        prompt="Review calc.py for correctness issues and briefly explain what you'd fix. Do not edit the file.",
        workspace=workspace,
        trace_log_path=trace_path,
        stage="code_review",
    )

    print("=" * 70)
    print("BOB RESULT")
    print("=" * 70)
    print(f"status:          {result.status}")
    print(f"task_id:         {result.task_id}")
    print(f"duration_ms:     {result.duration_ms}")
    print(f"session_cost:    {result.session_cost} Bobcoins")
    print(f"tool_calls:      {result.tool_calls}")
    print(f"trace cards written: {result.trace_cards_written}")

    print("\n" + "=" * 70)
    print("SIPA-TRACE (structured, diffable — read trace.jsonl for the real log)")
    print("=" * 70)
    log = TraceLog(trace_path)
    for card in log.cards():
        print(f"  seq={card.seq} stage={card.stage} action={card.action_type} "
              f"risk={card.risk_class.name} reversible={card.reversible}")

    print("\n" + "=" * 70)
    print("SIPA-SIGNAL (Bob's own explanation, cleaned)")
    print("=" * 70)
    sc = result.signal_card
    if sc:
        print(f"  original words:  {sc['original_word_count']}")
        print(f"  signal words:    {sc['signal_word_count']}")
        print(f"  noise level:     {sc['noise_level']}")
        print(f"  compression:     {sc['compression']:.0%}")
        print(f"  kept sentences:")
        for s in sc["kept_sentences"]:
            print(f"    - {s}")
        if sc["dropped_sentences"]:
            print(f"  dropped (pure filler):")
            for s in sc["dropped_sentences"]:
                print(f"    - {s}")
    else:
        print("  (no assistant text captured)")

    print("\n" + "=" * 70)
    print(f"Full trace: {trace_path}")
    print(f"Raw event count: {len(result.raw_events)}")


if __name__ == "__main__":
    main()
