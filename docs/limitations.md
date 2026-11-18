# Known limitations and release boundaries

- **Synthetic data only.** Outputs are not evidence of customer misconduct or a legal determination. This is not a sanctions-compliance control or transaction-monitoring system.
- **Geographic prevalence.** 165,479/180,346 signals (approximately 91.8%) were new-destination indicators. They may reflect first-observed exposure rather than genuine financial-crime risk. The first-observed-month check for geographic indicators returned zero; no institution-specific threshold calibration was performed.
- **Observation window.** Three prior calendar months are used for numerical baselines. Partial-month effects, low activity, synthetic distribution and unavailable earlier history can materially affect results.
- **Currency.** Monetary comparisons are within a currency using only positive amounts, not converted across currencies. Several currency-specific rows may be present for a single customer-month.
- **Source signal limitations.** No transaction-level identifiers or alert dispositions are included in the model prompt; it cannot confirm alleged matches, customer profiles, sanctions list accuracy or justifications.
- **Evidence nuance.** The model can infer unsupported negatives (e.g. 'no alerts'), overstate alert meaning, or conflate baseline means with preceding-month counts; four manual reviews found examples. Evidence IDs and Pydantic schemas are not semantic proof.
- **No production assurance.** No live AML/sanctions monitoring, dynamic watchlist retrieval, legal guidance, explainability validation for a learned model, drift measurement, robust adversarial evaluation, production authentication, access control, retention policy or institutional sign-off.
- **Data availability.** Original full synthetic datasets are not distributed, so public reproducibility is by code and independently supplied compatible data rather than bit-for-bit reconstruction of published totals.
- **Confidentiality.** Never use actual customer data or embed credentials in evidence prompts, repo files or published examples.
