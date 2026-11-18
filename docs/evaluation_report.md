# Evaluation report — four synthetic investigations (November 18, 2026)

## Evidence base
The author ran four scenarios, one with each of 1, 2, 3, and 4 **distinct indicator types**. Multiple rows may exist for one indicator type (for example, volume spikes in different currencies). The automated evaluator reported `STRUCTURE_PASS` for **all four cases**. A subsequent manual review of the supplied report summaries, findings and limitations identified interpretive wording problems; full input transactions were not independently inspected in that review.

| Customer/month | Types | Structural result | Manual narrative disposition |
|---|---:|---|---|
| C13648 / 2025-09-01 | 1 (two currency-specific volume rows) | PASS | Accept with qualifications |
| C12272 / 2025-10-01 | 2 (geography and volume, three rows) | PASS | Accept with qualifications |
| C10026 / 2025-05-01 | 3 | PASS | Accept with qualifications |
| C32144 / 2025-05-01 | 4 | PASS | Accept with minor wording caveat |

## Supported observations
- C13648: AED 69,028.51 vs 10,008.54 historical mean (6.90×); CNY 39,739.56 vs 10,598.78 (3.75×).
- C12272: one newly observed destination (USA); CHF 29,424.56 vs 3,417.82 (8.61×); USD 12,601.24 vs 4,150.08 (3.04×).
- C10026: frequency 5 vs prior monthly mean 1.0 (5.0×); new destinations Belarus and China; three screening alerts.
- C32144: frequency 6 vs 1.67 (3.60×); EUR 25,340.04 vs 7,299.91 (3.47×); new destinations Russia, UAE, UK; three screening alerts.

## Identified limitations / corrections to interpretation
1. Absence of an alert indicator **does not prove zero underlying alerts**. C13648/C12272 reports made unsupported 'no alerts' statements from the limited evidence (full transaction/alert records not supplied to LLM).
2. 'New destination' is relative to the observed source history, not proof of a comprehensive historical absence.
3. Baseline is a preceding **three-month mean**, not necessarily last month's exact count. C10026 narrative said 'rising from 1 to 5', which may mislead.
4. Three screening alerts need not represent three verified compliance concerns; alert causes and decisions were not present in LLM context.
5. A narrative claim about per-currency transaction count must be checked against `TransactionCount` in the complete evidence (C12272 excerpt omitted it).
6. Four cases do not establish generalisation, real-world detection performance, recall/precision, model safety or production suitability. Model-generated narratives remain subject to mandatory human review.

## Evaluation scope
Structural checks verified fields, identity, citation-ID membership, source-evidence equality, SHA-256 evidence fingerprint and required human review. **They do not semantically verify textual findings.** Human assessment was qualitative, on four synthetic outputs; no benchmark or blind annotator adjudication was performed. These findings are documented rather than triggering expansion of frozen v1 scope.
