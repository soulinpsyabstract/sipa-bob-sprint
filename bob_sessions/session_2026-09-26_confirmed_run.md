# Bob task session record — 2026-09-26 (real, verified run)

**Note on format:** this is a text record, not a GUI screenshot, because
IBM Bob 2.0 was run via CLI/Bob Shell on a headless server for this session
(the team's IDE access had setup issues at submission time). This documents
the same real, live Bob invocation the guide asks screenshots for.

- **Task ID:** `6b97a4360ede8290bbf159f8d7cd0fde`
- **Cost:** 0.144 Bobcoins (real spend, not simulated)
- **Task:** Bob read `calc.py` (sample file) and produced a code review
- **Tool calls:** 1 (`read_file`), classified `RiskClass.NONE` by
  `bob_harness/risk_map.py` — correct, read-only action
- **Hash-chain verification:** `VerifyResult(ok=True, count=1, problems=[])`
- **Output honesty check:** Bob's response text was run through
  `sipa-signal` before being accepted — classified `CLEAN`, 0% filler
  language detected
- **Source of record:** `HUB_GOVERNANCE/HACKATHONS__ACTIVE__2026-09-21.md`,
  confirmed live the same day this session ran, cross-checked against the
  actual harness code (`bob_harness/runner.py`, `bob_harness/risk_map.py`)
  in this repo.
