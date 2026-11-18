# Phase 4 — End-to-end report evaluation (v1)

## Fixed scope

Evaluate four synthetic customer-month cases: one each with **1, 2, 3, and 4 distinct indicator types**. The four-indicator case is `C32144 / 2025-05-01`, already generated and manually reviewed. The other three are chosen deterministically from the frozen 180,346-row signal export.

## Acceptance criteria

- Reports generated and saved successfully for four cases, without changing the frozen Risk Analytics Engine.
- Structural checks pass: report identity, source evidence equality, SHA-256 evidence fingerprint, valid evidence citations, mandatory human review, audit metadata.
- **Manual review** of all three newly generated reports for unsupported factual assertions, overinterpretation of screening alerts or geographic changes, correct units and baselines, and acknowledgement of missing context.
- Record manual findings and any limitations explicitly. Do not claim model accuracy or production readiness from four cases.

## Manual evidence review worksheet

| Customer/month | Source figures faithfully used? | Evidence citations correct? | Unsupported claims? | Appropriate limitations and human review? | Reviewer conclusion |
| --- | --- | --- | --- | --- | --- |
| 1-indicator case | Pending | Pending | Pending | Pending | Pending |
| 2-indicator case | Pending | Pending | Pending | Pending | Pending |
| 3-indicator case | Pending | Pending | Pending | Pending | Pending |
| C32144 / 2025-05-01 | Reviewed 2026-11-18 | Reviewed | One minor interpretive wording caveat | Yes | Accept with caveat |

Note: the supplied evaluator performs **structural checks**, not semantic verification of LLM narrative claims. Manual review is required before closing Phase 4.

## Public GitHub

Do not commit full local `data/validated/`, `data/outputs/`, generated reports, local API credentials, or virtual environments. Publish the evaluator, methodology, a **sanitised synthetic** example report if desired, and an aggregate evaluation summary with clear limitations.
