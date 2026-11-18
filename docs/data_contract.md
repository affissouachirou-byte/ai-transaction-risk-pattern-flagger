# Data contracts (v1)

**Transaction inputs**: required `TransactionID`, `CustomerID`, `BookingDate`, `Amount`, `Currency`, `DestinationCountry`. Additional source fields may include `ValueDate`, `PaymentChannel`, `OriginCountry`, `HighRiskJurisdiction` and expected alert labels. One row per unique `TransactionID` in the validated input. Source-derived `BookingDate` must be parseable; positive amounts are used for volume indicators.

**Screening alerts**: required `AlertID`, `CustomerID`, `TransactionID`, `CreatedDate`. The original synthetic alert schema also has `Watchlist`, `SimilarityScore`, `Threshold`, `Decision`, etc., but those fields do not enter the repeated-alert rule. One row per unique `AlertID`; each reference must resolve to a transaction with matching `CustomerID`. Alert month is determined from `CreatedDate`, potentially distinct from transaction month.

**Output signal grain**: (customer, month, indicator[, currency]); geography's `ObservedValue` is number of new destinations, frequency is transaction count, volume is summed positive amount for currency, repeated alerts is distinct AlertID count. `TransactionCount` and `AlertCount` are indicator-specific subsets and must not be summed across signals. Output fields: `CustomerID`, `Month`, `Indicator`, `ObservedValue`, `BaselineValue`, `Ratio`, `Currency`, `Evidence`, `TransactionCount`, `AlertCount`. Some numeric/currency values are null by design. No source TransactionIDs or AlertIDs are preserved at signal level.

**Portability**: the validated 995,905/200,000-record datasets were generated and prepared separately and are not provided. The small sample fixture in `data/samples` is illustrative and **not sufficient** to reproduce the recorded aggregate results.
