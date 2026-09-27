Full concept, open questions, and pre-sprint checklist (pre-kickoff):
https://claude.ai/code/artifact/490f5db8-1f5e-4fa5-a244-281a5f414444

# Bob Harness — IBM Bob 2.0 Hackathon

Use case (from the official example list): **Intelligent code review and
quality coach**. Bob does the review; this harness makes the review
verifiable and diffable instead of a paragraph you have to trust on read.

## What it does

`bob_harness/` runs `bob run --format stream-json` headlessly and turns the
stream into two artifacts:

1. **sipa-trace TraceLog** (`trace.jsonl`) — every tool call Bob makes
   becomes a hash-chained, risk-classified `TraceCard`. Deterministic
   rule-based risk classification (`sipa_trace.RiskClassifier`), not Bob
   grading its own actions. Verifiable end to end: `sipa_trace.verify()`
   walks the hash chain and confirms nothing in the log was altered after
   the fact.
2. **sipa-signal SignalCard** — Bob's own text explanation gets stripped of
   hedging/filler before a human reads it. Deterministic pattern match, not
   another model summarizing Bob's summary.

The tool→risk mapping (`bob_harness/risk_map.py`) is generic on purpose: it
classifies tool *capability* (does it write/delete/touch the network/touch
credentials), never the domain of the task Bob was given. Same classifier
works whatever repo Bob is pointed at.

## Layout

```
bob_harness/
  _pathsetup.py   — adds ../sipa-trace and ../sipa-signal to sys.path
                    (both zero-dependency pure-Python — no separate install
                    needed on the hackathon box)
  risk_map.py     — classify_tool_call(tool_name, params) -> ActionProfile
  runner.py       — run_bob_task(prompt, workspace, trace_log_path) -> BobRunResult
tests/
  test_risk_map.py — unit tests for the risk classifier, no live Bob calls
run_demo.py       — real end-to-end demo: calls `bob run` for real (spends
                    real Bobcoins), writes trace.jsonl, prints the SignalCard
bob_sessions/     — Task Session Summary PNG screenshots go here, one per
                    task, required for hackathon submission
```

## Running it

Requires `bob` CLI installed and authenticated.

On a normal machine with a browser, just use standard SSO login — it works
fine. The API-key auth workaround (env vars `BOBSHELL_API_KEY`/`BOB_API_KEY`)
is only needed on a headless server where the SSO flow hangs waiting for a
browser that doesn't exist; if that's not your situation, ignore it. That
workaround key is tied to a single hackathon account and isn't something to
request from a teammate — each person needs their own hackathon-provisioned
Bob account (see the official hackathon guide's account setup section) if
their IDE isn't showing the `ibm-coding-challenge-uat` instance.

```bash
# unit tests, no Bob calls, no cost
python3 -m pytest tests/ -v

# real end-to-end demo, spends real Bobcoins
python3 run_demo.py /tmp/some_workspace
```

Verified live 2026-09-26: `bob run` on a sample `calc.py`, 1 tool call
(`read_file`, correctly classified `RiskClass.NONE`), hash chain verified
(`VerifyResult(ok=True, count=1, problems=[])`), Bob's review text passed
through sipa-signal (classified `CLEAN`, 0% filler in this run — genuinely
clean text, not a fabricated pass).

## Team tracks (see governance doc section 8 for full detail)

- **Aelin** — this harness (Bob → sipa-trace → sipa-signal wiring)
- **Benjamin** — security review track: point Bob's Agent mode at a
  security review, classify findings via the risk_class scheme, document
  adversarial cases (attempts to get Bob to wave through something risky)
- **Abeeha** — findings aggregation track: use Bob's document understanding
  to summarize trace/signal output into a simple stats report (counts by
  risk category, noise stripped) — matches her stats background, no coding
  experience required
