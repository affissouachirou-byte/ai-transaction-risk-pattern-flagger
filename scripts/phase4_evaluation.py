"""Phase 4: small, reproducible AI report evaluation for frozen risk signals.

Run from the project root. Does not alter risk analytics or source data.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

import duckdb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ai_investigation import (  # noqa: E402
    InvestigationReport, generate_report, input_fingerprint, load_signals,
    save_report, validate_report,
)

SIGNALS = ROOT / "data/outputs/risk_signals_v1.parquet"
REPORT_DIR = ROOT / "data/outputs/investigations"
EVAL_DIR = ROOT / "evaluation"


def choose_cases() -> list[tuple[str, str, int]]:
    """One deterministic case with 1, 2, and 3 distinct indicator types."""
    with duckdb.connect() as con:
        rows = con.execute("""
            WITH per_case AS (
                SELECT CustomerID, CAST(Month AS DATE) AS Month,
                       COUNT(DISTINCT Indicator) AS IndicatorTypes,
                       COUNT(*) AS IndicatorRows
                FROM read_parquet(?)
                GROUP BY CustomerID, CAST(Month AS DATE)
            ), ranked AS (
                SELECT *, ROW_NUMBER() OVER (
                    PARTITION BY IndicatorTypes
                    ORDER BY IndicatorRows DESC, CustomerID, Month
                ) AS rn
                FROM per_case
                WHERE IndicatorTypes IN (1, 2, 3)
            )
            SELECT CustomerID, CAST(Month AS VARCHAR), IndicatorTypes
            FROM ranked WHERE rn = 1 ORDER BY IndicatorTypes
        """, [str(SIGNALS)]).fetchall()
    if len(rows) != 3:
        raise ValueError("Expected selectable cases with 1, 2, and 3 indicator types")
    return [(str(cid), str(month), int(n)) for cid, month, n in rows]


def reports_for_case(customer_id: str, month: str) -> list[Path]:
    return sorted(REPORT_DIR.glob(f"{customer_id}_{month}_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def check_report(path: Path, expected_customer: str, expected_month: str) -> dict:
    issues = []
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        audit = obj["audit"]
        evidence = obj["evidence"]
        report = InvestigationReport.model_validate(obj["report"])
        source = load_signals(SIGNALS, expected_customer, expected_month)
        # The evidence records and their ordering should be unchanged from the frozen export.
        if evidence != source:
            issues.append("Saved evidence differs from current frozen Parquet evidence")
        if audit.get("source_signal_sha256") != input_fingerprint(evidence):
            issues.append("Saved fingerprint does not match embedded evidence")
        if audit.get("source_signal_sha256") != input_fingerprint(source):
            issues.append("Saved fingerprint does not match source evidence")
        if audit.get("review_status") != "PENDING_HUMAN_REVIEW":
            issues.append("Unexpected review status")
        if audit.get("analytical_engine") != "Risk Analytics Engine v1 (frozen)":
            issues.append("Analytical engine version mismatch")
        if not audit.get("report_id") or not audit.get("generated_at_utc") or not audit.get("llm_model"):
            issues.append("Missing audit metadata")
        try:
            validate_report(report, source)
        except ValueError as e:
            issues.append(str(e))
        if report.human_review_required is not True:
            issues.append("Human review not required")
        cited = {id for finding in report.findings for id in finding.evidence_ids}
        supported = {s["evidence_id"] for s in source}
        if not cited.issubset(supported):
            issues.append("Unknown evidence reference")
        status = "STRUCTURE_PASS" if not issues else "STRUCTURE_FAIL"
        return {"customer_id": expected_customer, "month": expected_month,
                "file": str(path.relative_to(ROOT)), "indicator_rows": len(source),
                "findings": len(report.findings), "status": status,
                "issues": issues,
                "manual_review_required": True,
                "manual_review_completed": False}
    except Exception as e:
        return {"customer_id": expected_customer, "month": expected_month,
                "file": str(path.relative_to(ROOT)), "status": "STRUCTURE_FAIL",
                "issues": [f"{type(e).__name__}: {e}"],
                "manual_review_required": True, "manual_review_completed": False}


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate three diverse synthetic cases plus the initial four-indicator case")
    parser.add_argument("--generate", action="store_true", help="Generate up to 3 new LLM reports (uses API and may incur charges)")
    parser.add_argument("--model", default="gpt-4.1-mini")
    args = parser.parse_args()
    if not SIGNALS.is_file():
        raise FileNotFoundError(f"Missing frozen signal file: {SIGNALS}")

    cases = choose_cases()
    cases.append(("C32144", "2025-05-01", 4))
    print("Evaluation cases (one case per number of indicator types):")
    for cid, month, n in cases:
        print(f"  {cid} / {month} / {n} indicator type(s)")

    if args.generate:
        for cid, month, n in cases:
            if reports_for_case(cid, month):
                print(f"Reusing existing report: {cid} {month}")
                continue
            evidence = load_signals(SIGNALS, cid, month)
            report = generate_report(evidence, args.model)
            target = REPORT_DIR / f"{cid}_{month}_{uuid4().hex[:8]}.json"
            save_report(target, report, evidence, args.model)

    results = []
    for cid, month, n in cases:
        files = reports_for_case(cid, month)
        if not files:
            results.append({"customer_id": cid, "month": month,
                            "status": "NOT_GENERATED", "indicator_types": n,
                            "manual_review_required": True,
                            "manual_review_completed": False})
            continue
        result = check_report(files[0], cid, month)
        result["indicator_types"] = n
        results.append(result)
        print(f"{cid} {month}: {result['status']}")

    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    result_path = EVAL_DIR / "phase4_structural_results.json"
    result_path.write_text(json.dumps({
        "scope": "4 synthetic customer-month cases; automatic structural checks only",
        "semantic_accuracy_assessed": False,
        "results": results,
    }, indent=2), encoding="utf-8")
    print(f"Saved: {result_path}")
    if any(r["status"] == "STRUCTURE_FAIL" for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
