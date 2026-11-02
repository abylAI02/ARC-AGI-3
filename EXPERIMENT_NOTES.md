# Experiment notes

## Status

These are engineering smoke tests on a controlled synthetic environment. They are not evidence for stronger AI or quantum advantage.

## 64-world classical run

- Conditions: deterministic policy proxy and exact classical QAHS.
- Hidden worlds: all 64 combinations of the six binary rule dimensions.
- Result: both conditions solved 64/64 worlds in seven actions on average.
- Interpretation: the factorized representation, observation updates, exact objective, and termination logic are internally consistent. The environment is deliberately easy and therefore cannot distinguish the conditions.

## QAOA smoke runs

- QAOA configuration: statevector simulation, depth `p=2`, four COBYLA restarts, 100 optimizer evaluations per restart, and 1,024 shots per turn.
- Development worlds 0-3: 4/4 solved, 6.75 actions on average.
- Separate smoke worlds 4-7: 4/4 solved, seven actions on average.
- The non-integer average on worlds 0-3 came from one correct early guess. Four worlds are far too few to treat that as a performance improvement.
- An earlier low-budget QAOA configuration was unreliable. The formulation was corrected to encode observed rule values as explicit consistency penalties instead of weak tie-break terms. The current results must therefore be treated as post-development smoke tests, not held-out evidence.

## Remaining experimental requirements

1. Integrate a real LLM and freeze its prompt and output schema.
2. Replace the controlled rule-probe environment with several genuine ARC-like tasks.
3. Pre-register QAOA depth, optimizer budget, shots, penalty weights, seeds, and primary metrics.
4. Compare an actual LLM-only action choice against exact classical QAHS and QAOA-assisted QAHS using identical inputs.
5. Run enough held-out tasks and seeds to report uncertainty.
6. Measure circuit depth and transpiled resources in Qiskit; the current statevector engine estimates logical resources only.


## Mirror study: Claude Opus 5.5 on the GPT harness (pre-registered 2026-10-31)

**Question.** Is the live ARC-AGI-3 result (no condition clearly better) specific to `gpt-6-luna`, or does it hold for a different frontier model?

**Design.** Re-run the 9 published GPT live comparisons with `claude-opus-5-5` as the only change.
- Harness: commit `b57e381`, the code that produced the GPT runs (no reflection ledger; one proposal call per turn; no retries; fixed condition order; online only). It lives on branch `mirror/claude-on-gpt-harness`, which adds only `AnthropicJSONCaller`, `--provider`, and a model-name fix in the trace.
- Model settings: `ANTHROPIC_EFFORT=medium`, `max_tokens=16000`, adaptive thinking (always on), no temperature (not accepted by the model), no server-side model fallback. GPT settings were not recorded.
- Mode: online (`three.arcprize.org`), like the original runs.

| Game | Seed | Budget | GPT trace |
|---|---|---|---|
| ar25 | 0 | 20 | 20261029T152831Z |
| vc33 | 0 | 30 | 20261029T155621Z |
| lp85 | 0 | 30 | 20261029T163642Z |
| r11l | 0 | 20 | 20261029T170909Z |
| s5i5 | 0 | 20 | 20261029T173922Z |
| vc33 | 1 | 30 | 20261029T181132Z |
| ar25 | 1 | 20 | 20261029T182439Z |
| r11l | 1 | 20 | 20261029T184944Z |
| s5i5 | 1 | 20 | 20261029T184951Z (GPT failed before the first action in all conditions) |

**Metrics** (from `scripts/mirror_compare.py`). Primary: levels completed per condition. Secondary: actions used, distinct actions, how often the selected action is the top-utility one (GPT LLM-only: 151/216 on these 9 runs), and errors.

**Analysis rules.** Every run is reported, including failures; nothing is re-run except a run that fails before its first action because of an infrastructure error (ARC or API outage), which is re-run once and both attempts are reported. With 9 pairs, results are descriptive only.

**Known confounds.** The model's sampling settings are not comparable (GPT temperature and effort unknown). The online game version may have changed since 10/29. Wall time is not comparable.
