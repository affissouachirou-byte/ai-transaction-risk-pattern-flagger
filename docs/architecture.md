# Architecture and module boundaries

**Data layer**: read-only validated Databricks Delta tables -> PySpark normalisation -> four rule-based indicator DataFrames -> unified signal schema -> Parquet export. Source-table counts and source integrity were checked in the author's workspace; data is synthetic.

**AI layer**: local DuckDB query for a single `CustomerID`/month, records assigned S01… evidence identifiers -> JSON prompt -> OpenAI structured output parsed as `InvestigationReport` (Pydantic) -> identifier/citation checks -> JSON containing report, copied evidence and audit fields. Source signal fingerprint is SHA-256 of selected canonical JSON evidence rows, **not** a cryptographic hash of the entire Parquet file.

**Evaluation layer**: four customer-month cases selected by diversity of indicator types -> structural checks of schema, customer/month, evidence equality, fingerprint, cited IDs and human-review marker -> human reading of narratives, separately documented.

Runtime: validated PySpark phase on Databricks; validated local AI phase on Windows Python 3.11. Docker, model training, API service, streaming data, live watchlist retrieval and production deployment are not part of v1.
