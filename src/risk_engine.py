"""AI Transaction Risk Pattern Flagger — deterministic PySpark analytics v1.

The engine produces candidate investigation indicators, not confirmed misconduct.
No LLM is used in this component; LLM integration is a separate project phase.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F

# Portfolio prototype assumptions, not regulatory thresholds.
BASELINE_MONTHS = 3
MIN_PRIOR_TRANSACTIONS = 3
FREQUENCY_RATIO = 3.0
MIN_CURRENT_TRANSACTIONS = 5
VOLUME_RATIO = 3.0
MIN_MONTHLY_ALERTS = 3


def _month_calendar(spark: SparkSession, tx: DataFrame) -> DataFrame:
    bounds = tx.agg(F.min('Month').alias('min_m'), F.max('Month').alias('max_m')).first()
    if not bounds or bounds['min_m'] is None:
        raise ValueError('No valid BookingDate values in transaction dataset')
    lower, upper = bounds['min_m'], bounds['max_m']
    # Generate month rows entirely inside the JVM/Spark SQL engine.
    # spark.createDataFrame(Python_list) launches Python workers on Windows,
    # which can fail to connect even when Spark SQL operations work.
    return spark.sql(
        "SELECT explode(sequence("
        f"date'{lower.isoformat()}', date'{upper.isoformat()}', "
        "interval 1 month)) AS Month"
    )


def _require_fields(frame: DataFrame, fields: set[str], table: str) -> None:
    missing = fields - set(frame.columns)
    if missing:
        raise ValueError(f'{table} missing required fields: {sorted(missing)}')


def prepare_transactions(raw: DataFrame) -> DataFrame:
    """Exclude missing identifiers or unparseable booking times from risk calculations."""
    _require_fields(raw, {'TransactionID','CustomerID','BookingDate','Amount','Currency','DestinationCountry'}, 'transactions')
    tx = (raw
          .withColumn('BookingTS', F.to_timestamp('BookingDate'))
          .withColumn('Month', F.trunc(F.to_date('BookingTS'), 'month'))
          .withColumn('AmountNum', F.col('Amount').cast('double'))
          .withColumn('CurrencyNorm', F.upper(F.trim(F.col('Currency'))))
          .withColumn('DestinationNorm', F.upper(F.trim(F.col('DestinationCountry')))))
    return tx.filter(F.col('TransactionID').isNotNull() & F.col('CustomerID').isNotNull() & F.col('Month').isNotNull())


def prepare_alerts(raw: DataFrame) -> DataFrame:
    _require_fields(raw, {'AlertID','CustomerID','TransactionID','CreatedDate'}, 'alerts')
    return (raw
            .withColumn('AlertTS', F.to_timestamp('CreatedDate'))
            .withColumn('Month', F.trunc(F.to_date('AlertTS'), 'month'))
            .filter(F.col('AlertID').isNotNull() & F.col('CustomerID').isNotNull() & F.col('Month').isNotNull()))


def _signal(df: DataFrame, name: str, observed, baseline, ratio, currency, details, tx_count, alert_count) -> DataFrame:
    return df.select(
        F.col('CustomerID'), F.col('Month'), F.lit(name).alias('Indicator'),
        observed.cast('double').alias('ObservedValue'),
        baseline.cast('double').alias('BaselineValue'),
        ratio.cast('double').alias('Ratio'),
        currency.cast('string').alias('Currency'),
        details.cast('string').alias('Evidence'),
        tx_count.cast('long').alias('TransactionCount'),
        alert_count.cast('long').alias('AlertCount'),
    )


def detect_signals(spark: SparkSession, transaction_raw: DataFrame, alert_raw: DataFrame) -> DataFrame:
    tx = prepare_transactions(transaction_raw)
    alerts = prepare_alerts(alert_raw)
    months = _month_calendar(spark, tx)
    customer_months = tx.select('CustomerID').distinct().crossJoin(F.broadcast(months))
    historic_window = Window.partitionBy('CustomerID').orderBy('Month').rowsBetween(-BASELINE_MONTHS, -1)
    index_window = Window.partitionBy('CustomerID').orderBy('Month')

    # 1. Frequency, including zero-transaction months in historic baselines.
    counts = tx.groupBy('CustomerID', 'Month').agg(F.count('*').alias('N'))
    timeline = (customer_months.join(counts, ['CustomerID','Month'], 'left')
                .fillna({'N': 0})
                .withColumn('PriorN', F.sum('N').over(historic_window))
                .withColumn('HistoryMonths', F.row_number().over(index_window) - 1))
    freq = timeline.filter(
        (F.col('HistoryMonths') >= BASELINE_MONTHS) &
        (F.col('PriorN') >= MIN_PRIOR_TRANSACTIONS) &
        (F.col('N') >= MIN_CURRENT_TRANSACTIONS) &
        (F.col('N') >= F.col('PriorN') / F.lit(BASELINE_MONTHS) * F.lit(FREQUENCY_RATIO))
    )
    frequency = _signal(freq, 'FREQUENCY_SPIKE', F.col('N'),
                        F.col('PriorN') / F.lit(BASELINE_MONTHS),
                        F.col('N') / (F.col('PriorN') / F.lit(BASELINE_MONTHS)),
                        F.lit(None), F.lit('Current-month count versus average of preceding 3 calendar months'),
                        F.col('N'), F.lit(0))

    # 2. Volume spikes: only compare amounts in the SAME currency.
    positive_tx = tx.filter((F.col('AmountNum') > 0) & F.col('CurrencyNorm').isNotNull() & (F.col('CurrencyNorm') != ''))
    cust_currency = positive_tx.select('CustomerID','CurrencyNorm').distinct()
    currency_months = cust_currency.crossJoin(F.broadcast(months))
    cash = positive_tx.groupBy('CustomerID','CurrencyNorm','Month').agg(
        F.sum('AmountNum').alias('Amt'), F.count('*').alias('N'))
    cw = Window.partitionBy('CustomerID','CurrencyNorm').orderBy('Month').rowsBetween(-BASELINE_MONTHS, -1)
    ci = Window.partitionBy('CustomerID','CurrencyNorm').orderBy('Month')
    cash_timeline = (currency_months.join(cash, ['CustomerID','CurrencyNorm','Month'], 'left')
                     .fillna({'Amt': 0.0, 'N': 0})
                     .withColumn('PriorAmt', F.sum('Amt').over(cw))
                     .withColumn('PriorN', F.sum('N').over(cw))
                     .withColumn('HistoryMonths', F.row_number().over(ci) - 1))
    cash_spikes = cash_timeline.filter(
        (F.col('HistoryMonths') >= BASELINE_MONTHS) &
        (F.col('PriorN') >= MIN_PRIOR_TRANSACTIONS) &
        (F.col('PriorAmt') > 0) &
        (F.col('Amt') >= F.col('PriorAmt') / F.lit(BASELINE_MONTHS) * F.lit(VOLUME_RATIO)))
    volume = _signal(cash_spikes, 'VOLUME_SPIKE', F.col('Amt'),
                     F.col('PriorAmt') / F.lit(BASELINE_MONTHS),
                     F.col('Amt') / (F.col('PriorAmt') / F.lit(BASELINE_MONTHS)),
                     F.col('CurrencyNorm'), F.lit('Positive transaction amounts; same-currency comparison to prior 3 months'),
                     F.col('N'), F.lit(0))

    # 3. Newly observed destination country, against ALL preceding months.
    # Exclude first three months and customers without at least three past transactions.
    customer_history = timeline.select('CustomerID','Month','HistoryMonths','PriorN')
    # Count only transactions in the *first observed month* for a destination.
    # Counting all lifetime transactions here would incorrectly include future activity.
    destination_month = (tx.filter(F.col('DestinationNorm').isNotNull() & (F.col('DestinationNorm') != ''))
                         .groupBy('CustomerID', 'DestinationNorm', 'Month')
                         .agg(F.count('*').alias('DestinationTxCount')))
    country_window = Window.partitionBy('CustomerID', 'DestinationNorm')
    destinations = (destination_month
                    .withColumn('FirstObservedMonth', F.min('Month').over(country_window))
                    .filter(F.col('Month') == F.col('FirstObservedMonth'))
                    .drop('FirstObservedMonth'))
    newly_seen = (destinations.join(customer_history, ['CustomerID','Month'], 'inner')
                  .filter((F.col('HistoryMonths') >= BASELINE_MONTHS) & (F.col('PriorN') >= MIN_PRIOR_TRANSACTIONS))
                  .groupBy('CustomerID','Month')
                  .agg(F.sort_array(F.collect_set('DestinationNorm')).alias('NewCountries'),
                       F.sum('DestinationTxCount').alias('N')))
    geography = _signal(newly_seen, 'NEW_DESTINATION_COUNTRY', F.size('NewCountries'),
                        F.lit(None), F.lit(None), F.lit(None),
                        F.concat(F.lit('New destinations: '), F.concat_ws(', ', 'NewCountries')),
                        F.col('N'), F.lit(0))

    # 4. Repeated screening alerts within a calendar month; this is a volume
    # indicator, not a conclusion that any alert is a confirmed violation.
    alert_counts = alerts.groupBy('CustomerID','Month').agg(F.countDistinct('AlertID').alias('N'))
    repeated = alert_counts.filter(F.col('N') >= MIN_MONTHLY_ALERTS)
    repeated_alerts = _signal(repeated, 'REPEATED_SCREENING_ALERTS', F.col('N'),
                              F.lit(None), F.lit(None), F.lit(None),
                              F.lit('Multiple distinct screening alerts in the same calendar month'),
                              F.lit(0), F.col('N'))

    return (frequency.unionByName(volume)
            .unionByName(geography)
            .unionByName(repeated_alerts)
            .orderBy('CustomerID','Month','Indicator','Currency'))


def main() -> None:
    parser = argparse.ArgumentParser(description='Run deterministic FCC risk-pattern analytics')
    parser.add_argument('--data-dir', default='data/validated', help='Folder with local Parquet input files')
    parser.add_argument('--output', default='data/outputs/risk_signals_v1.parquet', help='Output Parquet directory')
    parser.add_argument('--master', default='local[4]', help='Spark master for local project execution')
    args = parser.parse_args()
    spark = (SparkSession.builder.master(args.master).appName('AITransactionRiskPatternFlagger')
             .config('spark.driver.memory', '4g')
             .config('spark.sql.shuffle.partitions', '8')
             .config('spark.sql.session.timeZone','UTC').getOrCreate())
    try:
        data_dir = Path(args.data_dir)
        transactions = spark.read.parquet(str(data_dir / 'transactions_clean.parquet'))
        alerts = spark.read.parquet(str(data_dir / 'alerts_linked.parquet'))
        signals = detect_signals(spark, transactions, alerts)
        if Path(args.output).exists():
            raise FileExistsError(f'Output already exists: {args.output}')
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        signals.write.mode('overwrite').parquet(args.output)
        print('Saved signals to:', args.output)
        signals.groupBy('Indicator').count().orderBy('Indicator').show(truncate=False)
    finally:
        spark.stop()


if __name__ == '__main__':
    main()
