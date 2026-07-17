# Unit Governance

Units are governed measurement metadata, not free-form labels. v1.4.0 seeds eighteen standard units and permits workspace-specific units when their dimension and conversion behavior are explicit.

## Standard registry

The seed registry covers common impact-measurement dimensions:

- dimensionless ratio and percent;
- counts;
- currency in USD;
- energy in kWh and MWh;
- mass in kg and tonnes;
- greenhouse gases in kgCO2e and tCO2e;
- distance in metres and kilometres;
- area in square metres and hectares;
- volume in litres and cubic metres;
- time in hours and days.

## Conversion model

Each unit declares a canonical unit, scale, offset, and output precision. Conversion uses an affine transform:

```text
canonical = value × scale_to_canonical + offset_to_canonical
result    = (canonical - target_offset) ÷ target_scale
```

A conversion is allowed only when source and target units have the same dimension. Cross-dimension conversions raise `UnitCompatibilityError` rather than silently returning a misleading number.

## Custom units

A custom unit must provide:

- stable code and display name;
- dimension;
- canonical unit reference;
- finite, non-zero conversion scale;
- finite offset;
- precision from 0 through 12 digits;
- lifecycle status and optional metadata.

Updates use optimistic concurrency. A stale expected revision is rejected.

## Comparability boundary

Compatible units are necessary but not sufficient for comparable indicators. Two values can share a unit while differing in population, geography, inclusion rules, measurement period, sampling design, source quality, or formula. Indicator and method definitions must carry those distinctions.
