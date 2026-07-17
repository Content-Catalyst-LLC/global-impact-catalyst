# Outcome Portfolios — v1.5.0

Outcome portfolios combine compatible observations across initiatives under explicit rules.

## Aggregation methods

Supported methods are sum, mean, weighted mean, minimum, and maximum. Portfolio members identify the initiative, indicator, optional result, weight, population scope, overlap group, and denominator definition.

## Guards

- **Period policy:** exact, same label, or overlapping periods.
- **Unit policy:** observations must be compatible with the portfolio target unit; conversions use the governed unit registry.
- **Missing-data policy:** exclude and disclose, include partial records, or fail.
- **Overlap policy:** exclude overlapping or unknown populations, allow with disclosure, or fail.

Every run records included and excluded members, warnings, rules, integrity counts, and a methodological boundary. Aggregation does not prove attribution and cannot eliminate double-counting risk beyond the information supplied by portfolio members.
