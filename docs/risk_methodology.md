# Risk analytics v1 — methodology and acceptance criteria

All four signals are **rules-based candidate investigation indicators**. No ML classifier has been trained and no LLM is used at this stage.

| Indicator | Grain | Required evidence | Illustrative threshold |
|---|---|---|---|
| FREQUENCY_SPIKE | Customer-month | Current count; previous 3-month mean; ratio | >=5 current and >=3 prior transactions and ratio >=3 |
| VOLUME_SPIKE | Customer-month-currency | Current positive amount; previous 3-month positive amount mean; ratio | >=3 prior same-currency transactions and ratio >=3 |
| NEW_DESTINATION_COUNTRY | Customer-month | Previously unseen destination(s) | >=3 prior transactions in 3 prior months; dataset history >=3 months |
| REPEATED_SCREENING_ALERTS | Customer-month | Distinct screening alert count | >=3 distinct alerts in month |

## Acceptance criteria

1. Reads local validated Parquet source files without altering either source.
2. Emits a stable, documented signal schema; output is a Parquet dataset directory.
3. Does not mix currencies in amount comparisons.
4. Historic signals do not use future transactions to calculate numeric baselines; geography uses earliest-observed destination month.
5. Avoids dividing by zero and enforces a minimum preceding-period history for temporal anomaly flags.
6. Preserves a direct `CustomerID`, month and indicator trail; LLM evidence selection is a subsequent phase.
7. Data and runtime issues are reported; no silent production readiness claim.

## Known constraints

- `CreatedDate` may fall outside transaction month coverage; screening-alert counts use alert month independently.
- First and last months may be partial months and influence ratios.
- Exclusions for invalid dates/identifiers are not yet logged as a data-quality report.
- Synthetic generation artifacts can produce apparent risk signals; evaluate before interpretation.
- Volume logic assumes numeric comparable amounts **within** each currency, and only positive amounts are included.
- Rules are intentionally simple for transparency; they are not regulatory rules or institution-calibrated detection thresholds.
