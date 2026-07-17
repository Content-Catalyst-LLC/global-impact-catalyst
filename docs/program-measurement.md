# Program Measurement — v1.5.0

The measurement repository stores time-indexed program records around the canonical impact contract. It does not replace the contract; it preserves operational history that would be inappropriate to compress into one snapshot.

## Observation states

Observations are explicitly marked `complete`, `missing`, `late`, `revised`, or `partial`. Missing records contain no value. Revised records point to the observation they supersede. Time-series views retain the revision chain while presenting the latest effective records.

## Disaggregation and denominators

Dimensions are aggregate descriptors such as geography, age band, delivery channel, or program site. Direct identifiers and nested person-level objects are rejected. Each observation can include a denominator definition so cost and rate calculations remain interpretable.

## Results and contribution context

Impact results are typed as outputs, outcomes, or long-term impacts. Directed relationships describe contribution, enablement, dependency, influence, or preconditions. External factors and contribution notes preserve alternative explanations, evidence references, and limitations.

## Exports

`export_measurement_repository(workspace_id)` produces the v1.5.0 measurement repository. It is embedded in the workspace bundle and restored idempotently with stable identifiers.
