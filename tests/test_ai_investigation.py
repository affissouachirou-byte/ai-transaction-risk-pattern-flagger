import sys
from pathlib import Path
from datetime import date
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from ai_investigation import (Finding, InvestigationReport, input_fingerprint, load_signals,
                              build_messages, validate_report)

@pytest.fixture
def signals():
    return [{"CustomerID": "C123", "Month": "2025-08-01", "Indicator": "FREQUENCY_SPIKE",
             "ObservedValue": 18.0, "BaselineValue": 5.0, "Ratio": 3.6, "Currency": None,
             "Evidence": "Current-month count versus average of preceding 3 calendar months",
             "TransactionCount": 18, "AlertCount": 0, "evidence_id": "S01"}]

def test_valid_evidence_reference(signals):
    report = InvestigationReport(customer_id="C123", month="2025-08-01", summary="More activity than baseline",
        findings=[Finding(observation="Frequency is higher", evidence_ids=["S01"])],
        review_questions=["Was this activity expected?"], limitations=["Synthetic data"],
        human_review_required=True)
    validate_report(report, signals)

def test_rejects_unknown_reference(signals):
    report = InvestigationReport(customer_id="C123", month="2025-08-01", summary="More activity than baseline",
        findings=[Finding(observation="Unsupported assertion", evidence_ids=["S99"])],
        review_questions=["Review?"], limitations=["Synthetic"], human_review_required=True)
    with pytest.raises(ValueError, match="unknown evidence"):
        validate_report(report, signals)

def test_rejects_wrong_customer(signals):
    report = InvestigationReport(customer_id="C999", month="2025-08-01", summary="More activity than baseline",
        findings=[Finding(observation="Frequency is higher", evidence_ids=["S01"])],
        review_questions=["Review?"], limitations=["Synthetic"], human_review_required=True)
    with pytest.raises(ValueError, match="does not match"):
        validate_report(report, signals)

def test_prompt_contains_expected_boundaries(signals):
    msgs = build_messages(signals)
    assert "Do not invent transactions" in msgs[0]["content"]
    assert "S01" in msgs[1]["content"]
    assert input_fingerprint(signals) == input_fingerprint(signals)

def test_local_parquet_query(tmp_path):
    import duckdb
    p = tmp_path / "signals.parquet"
    con = duckdb.connect()
    con.execute(f"""COPY (SELECT 'C123' AS CustomerID, DATE '2025-08-01' AS Month,
        'FREQUENCY_SPIKE' AS Indicator, 18.0 AS ObservedValue, 5.0 AS BaselineValue,
        3.6 AS Ratio, NULL::VARCHAR AS Currency, 'Observed frequency' AS Evidence,
        18::BIGINT AS TransactionCount, 0::BIGINT AS AlertCount)
        TO '{p.as_posix()}' (FORMAT PARQUET)""")
    con.close()
    rows = load_signals(p, 'C123', '2025-08-01')
    assert len(rows) == 1
    assert rows[0]['evidence_id'] == 'S01'
    assert rows[0]['Month'] == '2025-08-01'
