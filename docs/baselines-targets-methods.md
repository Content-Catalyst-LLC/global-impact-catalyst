# Baselines, Targets, Formulas, and Methods

v1.4.0 treats baselines, targets, formulas, and methods as versioned measurement objects rather than undocumented fields.

## Baseline models

Supported baseline types are:

- `point` — one selected observation;
- `average` — arithmetic mean of supplied observations;
- `rolling` — mean of the configured trailing window;
- `benchmark` — declared external reference value;
- `modelled` — value derived by a safe registered formula.

A baseline model records its unit, reference period, parameters, formula, quality profile, limitations, and immutable versions. Baseline computation returns the value, model type, observation count, and version identity used.

## Target models

Supported target types include:

- `absolute` — one target value;
- `range` — minimum and maximum accepted values;
- `relative` — change relative to a supplied baseline;
- `trajectory` — value evaluated over progress through a period;
- `formula` — custom expression using declared variables.

Trajectory types include linear, step, exponential, and custom formula. Milestones may record named period values without replacing the primary target model.

## Safe formula language

`gic-expression-1.0` accepts numerical constants, declared variable names, parentheses, and basic arithmetic operators. The parser rejects function calls, attribute access, indexing, comprehensions, imports, assignments, and all other executable Python syntax. Division by zero and non-finite results fail explicitly.

The formula language is intentionally narrow. It supports transparent derived calculations, not general-purpose scripting.

## Method definitions

A reusable method definition records:

- method name and design;
- description and version label;
- required inputs;
- quality dimensions and review notes;
- limitations and exclusions;
- lifecycle status;
- immutable content-hashed versions.

Methods describe how a value was produced. They do not guarantee that the design supports causal, comparative, or assurance claims.

## Governance

Updating a model or method creates a new immutable version. Registry bindings preserve the exact version associated with each initiative indicator. Human review remains required before changing definitions used in published or externally reported work.
