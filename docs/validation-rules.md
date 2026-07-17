# Validation Rules — v1.1.0

| Rule | Severity | Purpose |
|---|---|---|
| `GIC-REQ-001` | Error | Required initiative, goal, indicator, unit, periods, source, or method fact is missing |
| `GIC-UNIT-001` | Error | Baseline, observation, target, and indicator units differ |
| `GIC-UNIT-002` | Error | Unit label is multiline or excessively long |
| `GIC-PERIOD-001` | Error | Baseline occurs after the current observation |
| `GIC-PERIOD-002` | Warning | Period order cannot be inferred from labels |
| `GIC-TARGET-001` | Error | Baseline equals target, making progress undefined |
| `GIC-DIRECTION-001` | Error | Higher-is-better target is below baseline |
| `GIC-DIRECTION-002` | Error | Lower-is-better target is above baseline |
| `GIC-SOURCE-001` | Warning | Named source lacks a retrievable locator |
| `GIC-METHOD-001` | Warning | Method description is too brief for reproducibility |
| `GIC-CLAIM-001` | Error | Stronger claim lacks an explicit statement |
| `GIC-CLAIM-COMP-001` | Error | Comparison claim lacks an eligible design |
| `GIC-CLAIM-COMP-002` | Error | Comparison basis is missing |
| `GIC-CLAIM-CONTRIB-001` | Error | Contribution rationale is missing |
| `GIC-CLAIM-CONTRIB-002` | Warning | Monitoring-only design weakly supports contribution language |
| `GIC-CLAIM-CAUSAL-001` | Error | Causal claim lacks quasi-experimental or randomized design |
| `GIC-CLAIM-CAUSAL-002` | Error | Causal design metadata is missing |
| `GIC-CLAIM-CAUSAL-003` | Error | Causal claim confidence is not high |
| `GIC-CLAIM-CAUSAL-004` | Error | Causal claim has not completed review |

Rules are deterministic and shared by Python and JavaScript. A future release may add contextual registries for units, periods, indicators, and evidence profiles without changing the issue shape.
