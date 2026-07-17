# Methodology

Global Impact Catalyst is built around traceability, reproducibility, and explicit claim boundaries.

## Canonical path

```text
workspace → initiative → goal → outcome → indicator definition
→ baseline → observation → target → source → method
→ derived metric → interpretation → claim → review → revision → publication
```

## Progress formula

For higher-is-better indicators:

```text
(current − baseline) / (target − baseline) × 100
```

For lower-is-better indicators:

```text
(baseline − current) / (baseline − target) × 100
```

The engine rounds exported numeric results using decimal half-up behavior. Progress may be below 0 or above 100. Equal baseline and target values make progress undefined and produce a validation error.

## Facts and derivation

Entered facts are never relabeled as calculated evidence. Derived values record the engine, version, rounding rule, and formula so they can be reproduced. Interpretation text and claim eligibility remain separate from both facts and metrics.

## What validation does not do

Validation checks structural and semantic consistency. It does not authenticate a source, assess sampling validity, judge methodological fitness, verify an observation, establish attribution, or satisfy assurance and regulatory standards.
