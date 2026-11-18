# Reproducibility and runbook

## Reference run
- Databricks table inputs: `dbacademy.default.fcas_transactions_clean` (995,905 rows), `dbacademy.default.fcas_alerts_linked` (200,000 rows).
- Confirmed source integrity: 995,905 distinct transaction IDs, 200,000 distinct alert IDs, 0 orphan alerts, 0 cross-table CustomerID mismatches.
- Validated output: 180,346 rows stored in a Databricks volume as one Parquet part, transferred locally as `data/outputs/risk_signals_v1.parquet`.
- Four case reports saved locally under `data/outputs/investigations/`; raw reports are deliberately not public.

## Reproducing with a separate synthetic dataset
1. Supply schema-compatible synthetic transaction/alert data. Ensure transaction key uniqueness and alert foreign-key/customer consistency. The repository does not include the original full inputs.
2. Configure an accessible Databricks Unity Catalog volume and the two source table identifiers at the bottom of the notebook; replace the reference dataset count assertions with your own expected counts. Choose a fresh output directory: notebook deliberately fails if destination already exists.
3. Run in Databricks; review indicator breakdown and output count; download `risk_signals_v1.parquet` as a *file* rather than a directory.
4. On a local Python 3.11 machine, install `requirements.txt` in `.venv`, place the Parquet file under `data/outputs/`, and run:

   ```powershell
   .\.venv\Scripts\python.exe -m pytest tests -q
   .\.venv\Scripts\python.exe src\ai_investigation.py --customer-id YOUR_ID --month YYYY-MM-01 --dry-run
   .\.venv\Scripts\python.exe src\ai_investigation.py --customer-id YOUR_ID --month YYYY-MM-01
   ```

5. Use `scripts/phase4_evaluation.py` only against the reference signals file unless you adapt the hard-coded four-indicator case to your own test fixture.

## Environment and boundaries
The validated PySpark execution used Databricks after native Windows Spark produced a Hadoop-related Parquet writer error. A local Python/Spark runtime was started successfully but full pipeline execution was **not** validated there. Java 17 / Spark 3.5.7 were used during local exploration. Local AI processing uses DuckDB, OpenAI SDK and Pydantic. GitHub does not provide the original data or Databricks workspace; recreating the exact aggregate counts requires access to equivalent source data.
