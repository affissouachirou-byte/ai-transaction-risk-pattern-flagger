# AI Investigation Assistant — Scope and limitations

- **Source:** only the frozen Risk Analytics Engine v1 `risk_signals_v1.parquet` output (995,905 validated transactions and 200,000 linked alerts were inputs to the separate analytical engine).
- **Unit of analysis:** one `CustomerID` and one calendar month; a customer may have multiple currency-specific indicators and the model receives all indicator rows for that customer-month (maximum 30).
- **No re-scoring:** this component never changes thresholds or computes new risk indicators.
- **Grounding:** LLM is shown indicator metrics and Evidence text, not individual transactions or screening decisions. Findings must cite known evidence IDs. Program checks identifier scope, schema and cited IDs, **not semantic factual accuracy**.
- **Interpretation:** `NEW_DESTINATION_COUNTRY` describes a new observed destination, not a sanctions finding. `REPEATED_SCREENING_ALERTS` describes alert count, not a confirmed match. No inference of guilt or suspicious activity from an indicator alone.
- **Human oversight:** review is mandatory; outputs are drafts only. Investigators must independently check the original records and legal context.
- **Audit:** UTC timestamp, output UUID, source evidence fingerprint and exact evidence snapshot are stored in each report. Never store API keys in project artifacts.
- **Known limits:** no transaction-level citations in frozen signals, no customer risk profile, no dynamic sanctions lists, no calibration certification, no semantic hallucination detector, no external regulatory reasoning. All source data must be synthetic and verified before publication.
- **Publication:** exclude `data/validated/`, `data/outputs/`, `.venv/`, `.env`, and investigation reports. Only share code, tests, sample fixtures and aggregate non-identifying results.
