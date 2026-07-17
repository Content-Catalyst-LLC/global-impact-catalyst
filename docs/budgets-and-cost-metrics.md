# Budgets and Cost Metrics — v1.5.0

Financial records are typed as budgets, expenditures, commitments, or funding. Each record can identify a funding source, cost category, period, native currency, reporting currency, and explicit exchange rate.

Cross-currency records require a positive exchange rate. The system does not silently fetch or infer exchange rates. This keeps every converted amount reproducible from the saved record.

Cost metrics divide eligible expenditure records by a declared output, outcome, or beneficiary denominator. The result includes the numerator records, denominator definition, period, reporting currency, and exclusions. These ratios do not establish cost-effectiveness, efficiency, value for money, or causal attribution without additional design and review.
