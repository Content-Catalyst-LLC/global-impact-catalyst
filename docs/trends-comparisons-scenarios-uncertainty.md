# Trends, Comparisons, Scenarios, and Uncertainty

Global Impact Catalyst v1.7.0 adds a governed analytical repository over the existing canonical contracts, observations, target models, methods, units, evidence, and review records.

## Trend analysis

Trend runs select effective observations, apply explicit missing and partial-data policies, convert compatible units, and report first/last values, absolute and percentage change, slope, direction, minimum, maximum, and mean. Exclusions and blockers remain visible.

## Benchmarks and comparison sets

Benchmarks are revisioned records with indicator, unit, period, geography, population, source, method, and quality context. Comparison sets declare period, geography, population, missing-data, partial-data, and direction policies before ranking. Incompatible members are excluded rather than silently normalized.

## Scenarios and targets

Constant, linear, compound, and step models create conditional planning paths. A scenario may bind to an existing target model and expose a target gap for every projected point. Scenario output is not a forecast or causal estimate.

## Uncertainty and sensitivity

Absolute, relative, explicit-bound, and combined uncertainty models preserve assumptions and confidence labels. Sensitivity runs vary declared parameters and rank model responsiveness; they do not identify real-world causal importance.

## Persistence

Benchmarks, comparison sets and members, scenarios, uncertainty models, analysis runs, and sensitivity results are stored through migration 8 and exported in the v1.7.0 analysis repository and workspace bundle.
