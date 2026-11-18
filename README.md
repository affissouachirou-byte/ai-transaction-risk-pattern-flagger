# AI Transaction Risk Pattern Flagger

**Portfolio prototype · Python / PySpark / Databricks / DuckDB / OpenAI / Pydantic · Synthetic financial-crime data only**

A reproducible, explainable hybrid analytics-and-generative-AI workflow for financial-crime review support. Deterministic PySpark indicators flag unusual customer-month patterns; an LLM produces evidence-referenced *draft* investigation summaries. **No automated wrongdoing or sanctions-breach determinations are made. Human review is mandatory.**

## Verified project milestones (November 2026)

| Milestone | Recorded outcome |
|---|---|
| Source-data checks | 995,905 unique TransactionIDs; 200,000 unique AlertIDs; 0 unmatched alerts; 0 CustomerID mismatches |
| PySpark/Databricks analytics | 180,346 indicator rows written to Parquet |
| Distribution | 6,612 frequency; 5,378 volume; 165,479 new destination; 2,877 repeated screening alert rows |
| Local AI assistant | Successfully produced a report for C32144 / 2025-05-01 from 4 evidence rows |
| Four-case evaluation | 4/4 passed implemented structural checks; manual narrative review identified wording limitations |

**Caveat:** These are observations from a specific synthetic dataset and a four-report evaluation, not verified model performance on real-world cases. The geography indicator accounts for ~91.8% of indicator rows. Its first-customer-month validation returned zero signals, but more extensive calibration is outside v1 scope.

## Architecture

```text
Validated Delta tables (Databricks; synthetic)
  995,905 transactions ─────┐
                             ├─> Deterministic PySpark four-indicator engine
  200,000 linked alerts ────┘          │
                                      ▼
                             Frozen risk_signals_v1.parquet
                                      │
                                      ▼
                             DuckDB customer-month evidence selection
                                      │
                                      ▼
                             OpenAI structured report (Pydantic schema)
                                      │
                                      ▼
                             JSON report + evidence references + SHA-256 + human review
```

## Repository contents

- `notebooks/01_risk_analytics_databricks.py`: reference Databricks execution, **not** run automatically when imported. It reads the tables below and writes to a workspace-specific Unity Catalog volume.
- `src/risk_engine.py`: alternative local PySpark entry point; native Windows Parquet write failed in testing because Hadoop's `winutils.exe`/`HADOOP_HOME` were unavailable. **Databricks is the validated execution environment.**
- `src/ai_investigation.py`: local structured LLM investigation and offline `--dry-run`.
- `scripts/phase4_evaluation.py`: four-case report generation and structural validation.
- `docs/`: analytics methodology, AI methodology, evaluation evidence, architecture, limitations, release checklist.
- `data/samples/`: minimal **synthetic illustrative** CSV fixture; full datasets intentionally not distributed.

## Reproduce the analytical phase

1. Provide **your own synthetic** transaction and linked screening alert data with the schemas shown in `docs/data_contract.md`. The original 995,905/200,000-row data is not included in this public repository.
2. In Databricks, create/register cleaned Delta tables. The supplied reference notebook expects `dbacademy.default.fcas_transactions_clean` and `dbacademy.default.fcas_alerts_linked`; **edit the two source names, output volume path and reference count assertions** for your own workspace/data. See `docs/reproducibility.md`.
3. Run `notebooks/01_risk_analytics_databricks.py` as a Databricks notebook. It refuses to overwrite an existing output directory. Download the generated single Parquet file to `data/outputs/risk_signals_v1.parquet`.
4. Local AI setup with Python 3.11:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m pytest tests -q
   .\.venv\Scripts\python.exe src\ai_investigation.py --customer-id C32144 --month 2025-05-01 --dry-run
   ```

   The example case exists **only** if your signal export contains it. Replace it with a case from your own data. `--dry-run` does not contact the OpenAI API.
5. Set `OPENAI_API_KEY` in your shell's environment (never commit it) and omit `--dry-run` to produce the JSON report. API calls may incur charges. For a fixed four-case assessment using the reference dataset, run `python scripts/phase4_evaluation.py --generate` from project root. The script assumes the reference data's C32144 case; other datasets need a revised evaluation fixture.

## Interpretation and limitations

Indicators are *candidate review signals*, **not** validated predictive models or legally established breaches. Source alerts are sanctions/watchlist-screening events; they are not equivalent to AML-monitoring alerts or confirmed positives. Alert decisions, customer KYC profiles and transaction-level documents are **not included** in the LLM context. Structural schema/citation checks do not verify all narrative claims. See `docs/limitations.md` and `docs/evaluation_report.md`.

## Public sharing

Never commit real banking/client data, API keys, full datasets, investigation outputs, personal work files or virtual environments. `data/validated/` and `data/outputs/` are ignored. Verify tracked file contents and Git history before changing the repository to public.

**Status:** portfolio prototype; analytics frozen for integration; four synthetic AI reports evaluated; not production-ready.
